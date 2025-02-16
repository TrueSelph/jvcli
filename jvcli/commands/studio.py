"""Studio command group for deploying and interfacing with the Jivas Studio."""

import json
from pathlib import Path

import click
import jaclang  # noqa: F401
from bson import ObjectId
from jac_cloud.core.architype import NodeAnchor
from uvicorn import run


@click.group()
def studio() -> None:
    """Group for managing Jivas Studio resources."""
    pass  # pragma: no cover


def get_graph(root: str) -> dict:
    """Fetches a graph structure from the database."""
    nodes = []
    edges = []

    edge_collection = NodeAnchor.Collection.get_collection("edge")
    node_collection = NodeAnchor.Collection.get_collection("node")
    node_docs = node_collection.find({"root": ObjectId(root)})
    edge_docs = edge_collection.find({"root": ObjectId(root)})

    for node in node_docs:
        nodes.append(
            {
                "id": node["_id"],
                "data": node["architype"],
                "name": node["name"],
            }
        )
    for edge in edge_docs:
        edges.append(
            {
                "id": edge["_id"],
                "name": edge["name"],
                "source": edge["source"],
                "target": edge["target"],
                "data": edge["architype"],
            }
        )

    return {
        "nodes": json.loads(json.dumps(nodes, default=str)),
        "edges": json.loads(json.dumps(edges, default=str)),
    }


def get_users() -> list:
    """Fetches users from the database."""
    users = []
    user_collection = NodeAnchor.Collection.get_collection("user")
    user_docs = user_collection.find()

    for user in user_docs:
        users.append(
            {
                "id": user["_id"],
                "root_id": user["root_id"],
                "email": user["email"],
            }
        )

    return json.loads(json.dumps(users, default=str))


@studio.command()
@click.option("--port", default=8989, help="Port for the studio to launch on.")
def launch(port: int) -> None:
    """Launch the Jivas Studio on the specified port."""
    click.echo(f"Launching Jivas Studio on port {port}...")
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles

    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_api_route("/graph", endpoint=get_graph, methods=["GET"])
    app.add_api_route("/users", endpoint=get_users, methods=["GET"])

    client_dir = Path(__file__).resolve().parent.parent.joinpath("studio")
    app.mount("/", StaticFiles(directory=client_dir, html=True), name="studio")

    run(app, host="0.0.0.0", port=port)
