"""Studio command group for deploying and interfacing with the Jivas Studio."""

import click
import jaclang  # Import is necessary to load the plugin
from uvicorn import run
from bson import ObjectId
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from jac_cloud.core.architype import NodeAnchor
from fastapi.middleware.cors import CORSMiddleware
from jac_cloud.jaseci.security import decrypt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
import json


def get_nodes_and_edges(
    nid: str,
    current_depth: int,
    depth: int,
    nodes: list,
    edges: list,
    node_collection,
    edge_collection,
):
    if current_depth >= depth:
        return

    outgoing_edges = edge_collection.find(
        {
            "$or": [
                {"source": nid},
                {"source": {"$regex": f"{nid}$"}},
            ]
        }
    )

    for edge in outgoing_edges:
        edges.append(
            {
                "id": edge["_id"],
                "name": edge["name"],
                "source": edge["source"],
                "target": edge["target"],
                "data": edge["architype"],
            }
        )

        node_id = edge["target"].split(":")[-1]
        connected_nodes = node_collection.find({"_id": ObjectId(node_id)})

        for node in connected_nodes:
            nodes.append(
                {
                    "id": node["_id"],
                    "data": node["architype"],
                    "name": node["name"],
                }
            )

            get_nodes_and_edges(
                node["_id"],
                current_depth + 1,
                depth,
                nodes,
                edges,
                node_collection,
                edge_collection,
            )


# need this because endpoint annotation differs depending on require auth flag
class EndpointFactory:
    @staticmethod
    def create_endpoints(require_auth: bool, security: HTTPBearer | None):
        def validate_auth(credentials: HTTPAuthorizationCredentials):
            """Validate authentication token."""
            token = credentials.credentials
            if not token or not decrypt(token):
                raise HTTPException(status_code=401, detail="Invalid token")

        def get_graph_data(root: str):
            """Get graph nodes and edges data."""
            edge_collection = NodeAnchor.Collection.get_collection("edge")
            node_collection = NodeAnchor.Collection.get_collection("node")

            nodes = [
                {
                    "id": node["_id"],
                    "data": node["architype"],
                    "name": node["name"],
                }
                for node in node_collection.find({"root": ObjectId(root)})
            ]

            edges = [
                {
                    "id": edge["_id"],
                    "name": edge["name"],
                    "source": edge["source"],
                    "target": edge["target"],
                    "data": edge["architype"],
                }
                for edge in edge_collection.find({"root": ObjectId(root)})
            ]

            return {"nodes": nodes, "edges": edges}

        def get_users_data():
            """Get users data."""
            user_collection = NodeAnchor.Collection.get_collection("user")
            return [
                {
                    "id": user["_id"],
                    "root_id": user["root_id"],
                    "email": user["email"],
                }
                for user in user_collection.find()
            ]

        def get_node_connections(node_id: str, depth: int):
            nid = node_id.split(":")[-1]
            current_depth = 0
            nodes = []
            edges = []

            edge_collection = NodeAnchor.Collection.get_collection("edge")
            node_collection = NodeAnchor.Collection.get_collection("node")

            get_nodes_and_edges(
                nid,
                current_depth,
                depth,
                nodes,
                edges,
                node_collection,
                edge_collection,
            )

            return {"nodes": nodes, "edges": edges}

        if not require_auth:

            async def graph_endpoint(root: str):
                return JSONResponse(
                    content=json.loads(json.dumps(get_graph_data(root), default=str))
                )

            async def users_endpoint():
                return JSONResponse(
                    content=json.loads(json.dumps(get_users_data(), default=str))
                )

            async def node_endpoint(node_id: str, depth: int):
                return JSONResponse(
                    content=json.loads(
                        json.dumps(get_node_connections(node_id, depth), default=str)
                    )
                )

            return graph_endpoint, users_endpoint, node_endpoint

        else:

            async def guarded_graph_endpoint(
                root: str,
                credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
            ):
                validate_auth(credentials)
                return JSONResponse(
                    content=json.loads(json.dumps(get_graph_data(root), default=str))
                )

            async def guarded_users_endpoint(
                credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
            ):
                validate_auth(credentials)
                return JSONResponse(
                    content=json.loads(json.dumps(get_users_data(), default=str))
                )

            async def guarded_node_endpoint(
                node_id: str,
                depth: int,
                credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
            ):
                validate_auth(credentials)
                return JSONResponse(
                    content=json.loads(
                        json.dumps(get_node_connections(node_id, depth), default=str)
                    )
                )

            return guarded_graph_endpoint, guarded_users_endpoint, guarded_node_endpoint


@click.group()
def studio():
    """Group for managing Jivas Studio resources."""
    pass


@studio.command()
@click.option("--port", default=8989, help="Port for the studio to launch on.")
@click.option(
    "--require-auth", default=False, help="Require authentication for studio api."
)
def launch(port, require_auth):
    """Launch the Jivas Studio on the specified port."""
    click.echo(f"Launching Jivas Studio on port {port}...")

    security = HTTPBearer() if require_auth else None

    get_graph, get_users, get_node = EndpointFactory.create_endpoints(
        require_auth, security
    )

    app = FastAPI(title="Jivas Studio API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_api_route("/graph", endpoint=get_graph, methods=["GET"])
    app.add_api_route("/users", endpoint=get_users, methods=["GET"])
    app.add_api_route("/graph/node", endpoint=get_node, methods=["GET"])

    client_dir = (
        Path(__file__)
        .resolve()
        .parent.parent.joinpath("client-auth" if require_auth else "client")
    )

    app.mount(
        "/",
        StaticFiles(directory=client_dir, html=True),
        name="studio",
    )

    app.mount(
        "/graph",
        StaticFiles(directory=client_dir, html=True),
        name="studio_graph",
    )

    run(app, host="0.0.0.0", port=port)
