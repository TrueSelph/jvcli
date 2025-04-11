"""This module contains utility functions for the JVCLI client."""

import base64
import json
import os
from importlib.util import module_from_spec, spec_from_file_location
from io import BytesIO
from typing import Any, Callable, Dict, List, Optional

import requests
import streamlit as st
import yaml
from PIL import Image

JIVAS_BASE_URL = os.environ.get("JIVAS_BASE_URL", "http://localhost:8000")


def load_function(file_path: str, function_name: str, **kwargs: Any) -> Callable:
    """Dynamically loads and returns a function from a Python file, with optional keyword arguments."""

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No file found at {file_path}")

    # Get the module name from the file name
    module_name = os.path.splitext(os.path.basename(file_path))[0]

    # Load the module specification
    spec = spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"Could not load specification for module {module_name}")

    # Create the module
    module = module_from_spec(spec)
    if spec.loader is None:
        raise ImportError(f"Could not load module {module_name}")

    # Execute the module
    spec.loader.exec_module(module)

    # Get the function
    if not hasattr(module, function_name):
        raise AttributeError(f"Function '{function_name}' not found in {file_path}")

    func = getattr(module, function_name)

    # Ensure the returned callable can accept any kwargs passed to it
    def wrapped_func(*args: Any, **func_kwargs: Any) -> Any:
        return func(*args, **{**kwargs, **func_kwargs})

    return wrapped_func


def call_action_walker_exec(
    agent_id: str,
    module_root: str,
    walker: str,
    args: Optional[Dict] = None,
    files: Optional[List] = None,
    headers: Optional[Dict] = None,
) -> list:
    """Call the API to execute a walker action for a given agent."""

    ctx = get_user_info()

    endpoint = f"{JIVAS_BASE_URL}/action/walker"

    if ctx.get("token"):
        try:
            headers = headers if headers else {}
            headers["Authorization"] = "Bearer " + ctx["token"]

            # Create form data
            data = {"agent_id": agent_id, "module_root": module_root, "walker": walker}

            if args:
                data["args"] = json.dumps(args)

            file_list = []

            if files:

                for file in files:
                    file_list.append(("attachments", (file[0], file[1], file[2])))

            # Dispatch request
            response = requests.post(
                url=endpoint, headers=headers, data=data, files=file_list
            )

            if response.status_code == 200:
                result = response.json()
                return result if result else []

            if response.status_code == 401:
                st.session_state.EXPIRATION = ""
                return []

        except Exception as e:
            st.session_state.EXPIRATION = ""
            st.write(e)

    return []


def call_api(
    endpoint: str,
    method: str = "POST",
    headers: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
    files: Optional[List] = None,
) -> Optional[Dict]:
    """Generic function to call an API endpoint."""
    ctx = get_user_info()

    if ctx.get("token"):
        try:
            headers = headers if headers else {}
            headers["Authorization"] = "Bearer " + ctx["token"]

            if method == "POST":
                response = requests.post(
                    endpoint, headers=headers, json=json_data, files=files
                )
            elif method == "GET":
                response = requests.get(endpoint, headers=headers, params=json_data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            if response.status_code == 401:
                st.session_state.EXPIRATION = ""
                return None

            if response.status_code in [200, 501, 503]:
                return response.json()

        except Exception as e:
            st.session_state.EXPIRATION = ""
            st.write(e)

    return None


def call_healthcheck(agent_id: str, headers: Optional[Dict] = None) -> dict:
    """Call the API to check the health of an agent."""
    endpoint = f"{JIVAS_BASE_URL}/walker/healthcheck"
    json_data = {"agent_id": agent_id}
    result = call_api(endpoint, headers=headers, json_data=json_data)
    if result:
        reports = result.get("reports", [])
        return reports[0] if reports else {}
    return {}


def call_list_agents() -> list:
    """Call the API to list agents."""
    endpoint = f"{JIVAS_BASE_URL}/walker/list_agents"
    json_data = {"reporting": True}
    result = call_api(endpoint, json_data=json_data)
    if result:
        reports = result.get("reports", [])
        return [{"id": agent["id"], "label": agent["name"]} for agent in reports]
    return []


def call_get_agent(agent_id: str) -> dict:
    """Call the API to get details of a specific agent."""
    endpoint = f"{JIVAS_BASE_URL}/walker/get_agent"
    json_data = {"agent_id": agent_id}
    result = call_api(endpoint, json_data=json_data)
    if result:
        reports = result.get("reports", [])
        return reports[0] if reports else {}
    return {}


def call_list_actions(agent_id: str) -> list:
    """Call the API to list actions for a given agent."""
    endpoint = f"{JIVAS_BASE_URL}/walker/list_actions"
    json_data = {"agent_id": agent_id}
    result = call_api(endpoint, json_data=json_data)
    if result:
        reports = result.get("reports", [])
        return reports[0] if reports else []
    return []


def call_get_action(agent_id: str, action_id: str) -> list:
    """Call the API to get a specific action for a given agent."""
    endpoint = f"{JIVAS_BASE_URL}/walker/get_action"
    json_data = {"agent_id": agent_id, "action_id": action_id}
    result = call_api(endpoint, json_data=json_data)
    if result:
        reports = result.get("reports", [])
        return reports[0] if reports else []
    return []


def call_update_action(agent_id: str, action_id: str, action_data: dict) -> dict:
    """Call the API to update a specific action for a given agent."""
    endpoint = f"{JIVAS_BASE_URL}/walker/update_action"
    json_data = {
        "agent_id": agent_id,
        "action_id": action_id,
        "action_data": action_data,
    }
    result = call_api(endpoint, json_data=json_data)
    if result:
        reports = result.get("reports", [])
        return reports[0] if reports else {}
    return {}


def call_update_agent(
    agent_id: str, agent_data: dict, with_actions: bool = False
) -> dict:
    """Call the API to update a specific agent."""
    endpoint = f"{JIVAS_BASE_URL}/walker/update_agent"
    json_data = {"agent_id": agent_id, "agent_data": agent_data}
    result = call_api(endpoint, json_data=json_data)
    if result:
        reports = result.get("reports", [])
        return reports[0] if reports else {}
    return {}


def call_import_agent(descriptor: str, headers: Optional[Dict] = None) -> list:
    """Call the API to import an agent."""
    endpoint = f"{JIVAS_BASE_URL}/walker/import_agent"
    json_data = {"descriptor": descriptor}
    result = call_api(endpoint, headers=headers, json_data=json_data)
    if result:
        reports = result.get("reports", [])
        return reports[0] if reports else []
    return []


def get_user_info() -> dict:
    """Get user information from the session state."""
    return {
        "root_id": st.session_state.get("ROOT_ID", ""),
        "token": st.session_state.get("TOKEN", ""),
        "expiration": st.session_state.get("EXPIRATION", ""),
    }


def decode_base64_image(base64_string: str) -> Image:
    """Decode a base64 string into an image."""
    # Decode the base64 string
    image_data = base64.b64decode(base64_string)

    # Create a bytes buffer from the decoded bytes
    image_buffer = BytesIO(image_data)

    # Open the image using PIL
    return Image.open(image_buffer)


class LongStringDumper(yaml.SafeDumper):
    """Custom YAML dumper to handle long strings."""

    def represent_scalar(
        self, tag: str, value: str, style: Optional[str] = None
    ) -> yaml.ScalarNode:
        """Represent scalar values, using block style for long strings."""
        # Replace any escape sequences to format the output as desired
        if (
            len(value) > 150 or "\n" in value
        ):  # Adjust the threshold for long strings as needed
            style = "|"
            # converts all newline escapes to actual representations
            value = "\n".join([line.rstrip() for line in value.split("\n")])
        else:
            # converts all newline escapes to actual representations
            value = "\n".join([line.rstrip() for line in value.split("\n")]).rstrip()

        return super().represent_scalar(tag, value, style)


def jac_yaml_dumper(
    data: Any,
    indent: int = 2,
    default_flow_style: bool = False,
    allow_unicode: bool = True,
    sort_keys: bool = False,
) -> str:
    """Dumps YAML data using LongStringDumper with customizable options."""
    return yaml.dump(
        data,
        Dumper=LongStringDumper,
        indent=indent,
        default_flow_style=default_flow_style,
        allow_unicode=allow_unicode,
        sort_keys=sort_keys,
    )
