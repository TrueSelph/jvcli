"""Streamlit widgets for JVCLI client app."""

from typing import Any, List, Optional, Tuple

import streamlit as st
import yaml
from streamlit_elements import mui

from jvcli.client.lib.utils import call_get_action, call_update_action


def app_header(agent_id: str, action_id: str, info: dict) -> tuple:
    """Render the app header and return model key and module root."""

    # Create a dynamic key for the session state using the action_id
    model_key = f"model_{agent_id}_{action_id}"
    module_root = info.get("config", {}).get("module_root")

    # Initialize session state if not already
    if model_key not in st.session_state:
        # Copy original data to prevent modification of original_data
        st.session_state[model_key] = call_get_action(
            agent_id=agent_id, action_id=action_id
        )

    # add standard action app header
    st.header(
        st.session_state[model_key]
        .get("_package", {})
        .get("meta", {})
        .get("title", "Action"),
        divider=True,
    )

    # Display the description from the model
    if description := st.session_state[model_key].get("description", False):
        st.text(description)

    # Manage the 'enabled' field
    st.session_state[model_key]["enabled"] = st.checkbox(
        "Enabled", key="enabled", value=st.session_state[model_key]["enabled"]
    )

    return model_key, module_root


def snake_to_title(snake_str: str) -> str:
    """Convert a snake_case string to Title Case."""
    return snake_str.replace("_", " ").title()


def app_controls(agent_id: str, action_id: str) -> None:
    """Render the app controls for a given agent and action."""
    # Generate a dynamic key for the session state using the action_id
    model_key = f"model_{agent_id}_{action_id}"

    # Recursive function to handle nested dictionaries
    def render_fields(item_key: str, value: Any, parent_key: str = "") -> None:
        """Render fields based on their type."""

        field_type = type(value)
        label = snake_to_title(item_key)  # Convert item_key to Title Case

        if item_key not in st.session_state.get("model_key", {}).keys():
            # Special case for 'api_key' to render as a password field
            if item_key == "api_key":
                st.session_state[model_key][item_key] = st.text_input(
                    label, value=value, type="password", key=item_key
                )

            elif field_type == int:
                st.session_state[model_key][item_key] = st.number_input(
                    label, value=value, step=1, key=item_key
                )

            elif field_type == float:
                st.session_state[model_key][item_key] = st.number_input(
                    label, value=value, step=0.01, key=item_key
                )

            elif field_type == bool:
                st.session_state[model_key][item_key] = st.checkbox(
                    label, value=value, key=item_key
                )

            elif field_type == list:
                yaml_str = st.text_area(
                    label + " (YAML format)", value=yaml.dump(value), key=item_key
                )
                try:
                    # Update the list with the user-defined YAML
                    loaded_value = yaml.safe_load(yaml_str)
                    if not isinstance(loaded_value, list):
                        raise ValueError("The provided YAML does not produce a list.")
                    st.session_state[model_key][item_key] = loaded_value
                except (yaml.YAMLError, ValueError) as e:
                    st.error(f"Error parsing YAML for {item_key}: {e}")

            elif field_type == str:
                if len(value) > 100:
                    st.session_state[model_key][item_key] = st.text_area(
                        label, value=value, key=item_key
                    )
                else:
                    st.session_state[model_key][item_key] = st.text_input(
                        label, value=value, key=item_key
                    )

            elif field_type == dict:
                yaml_str = st.text_area(
                    label + " (YAML format)", value=yaml.dump(value), key=item_key
                )
                try:
                    # Update the dictionary with the user-defined YAML
                    st.session_state[model_key][item_key] = (
                        yaml.safe_load(yaml_str) or {}
                    )
                except yaml.YAMLError as e:
                    st.error(f"Error parsing YAML for {item_key}: {e}")

            else:
                st.write(f"Unsupported type for {item_key}: {field_type}")

    # Iterate over keys of context except specific keys
    keys_to_iterate = [
        key
        for key in (st.session_state[model_key]).keys()
        if key not in ["id", "version", "label", "description", "enabled", "_package"]
    ]

    for item_key in keys_to_iterate:
        render_fields(item_key, st.session_state[model_key][item_key])


def app_update_action(agent_id: str, action_id: str) -> None:
    """Add a standard update button to apply changes."""

    model_key = f"model_{agent_id}_{action_id}"

    st.divider()

    if st.button("Update"):
        result = call_update_action(
            agent_id=agent_id,
            action_id=action_id,
            action_data=st.session_state[model_key],
        )
        if result and result.get("id", "") == action_id:
            st.success("Changes saved")
        else:
            st.error("Unable to save changes")


def dynamic_form(
    field_definitions: list,
    initial_data: Optional[list] = None,
    session_key: str = "dynamic_form",
) -> list:
    """
    Create a dynamic form widget with add/remove functionality.

    Parameters:
    - field_definitions: A list of dictionaries where each dictionary defines a field
                         with 'name', 'type', and any specific 'options' if needed.
    - initial_data: A list of dictionaries to initialize the form with predefined values.
    - session_key: A unique key to store and manage session state of the form.

    Returns:
    - list: The current value of the dynamic form.
    """
    if session_key not in st.session_state:
        if initial_data is not None:
            st.session_state[session_key] = []
            for idx, row_data in enumerate(initial_data):
                fields = {
                    field["name"]: row_data.get(field["name"], "")
                    for field in field_definitions
                }
                st.session_state[session_key].append({"id": idx, "fields": fields})
        else:
            st.session_state[session_key] = [
                {"id": 0, "fields": {field["name"]: "" for field in field_definitions}}
            ]

    def add_row() -> None:
        """Add a new row to the dynamic form."""
        new_id = (
            max((item["id"] for item in st.session_state[session_key]), default=-1) + 1
        )
        new_row = {
            "id": new_id,
            "fields": {field["name"]: "" for field in field_definitions},
        }
        st.session_state[session_key].append(new_row)

    def remove_row(id_to_remove: int) -> None:
        """Remove a row from the dynamic form."""
        st.session_state[session_key] = [
            item for item in st.session_state[session_key] if item["id"] != id_to_remove
        ]

    for item in st.session_state[session_key]:
        # Display fields in a row
        row_cols = st.columns(len(field_definitions))
        for i, field in enumerate(field_definitions):
            field_name = field["name"]
            field_type = field.get("type", "text")
            options = field.get("options", [])

            if field_type == "text":
                item["fields"][field_name] = row_cols[i].text_input(
                    field_name,
                    value=item["fields"][field_name],
                    key=f"{session_key}_{item['id']}_{field_name}",
                )
            elif field_type == "number":
                item["fields"][field_name] = row_cols[i].number_input(
                    field_name,
                    value=int(item["fields"][field_name]),
                    key=f"{session_key}_{item['id']}_{field_name}",
                )
            elif field_type == "select":
                item["fields"][field_name] = row_cols[i].selectbox(
                    field_name,
                    options,
                    index=(
                        options.index(item["fields"][field_name])
                        if item["fields"][field_name] in options
                        else 0
                    ),
                    key=f"{session_key}_{item['id']}_{field_name}",
                )

        # Add a remove button in a new row beneath the fields, aligned to the left
        with st.container():
            if st.button(
                "Remove",
                key=f"remove_{item['id']}",
                on_click=lambda id=item["id"]: remove_row(id),
            ):
                pass

    # Add a divider above the "Add Row" button
    st.divider()

    # Button to add a new row
    st.button("Add Row", on_click=add_row)

    # Return the current value of the dynamic form
    return [item["fields"] for item in st.session_state[session_key]]


def card_grid(cards_data: List[dict], columns: int = 3) -> None:
    """
    Display a grid of cards with titles, bodies, and footers.

    Parameters:
    - cards_data: A list where each element is a dictionary representing a card.
                  Each dictionary should have keys 'title', 'body', and 'footer'.
                  'body' is a list of dictionaries with 'label' and 'value'.
                  'footer' is a list of dictionaries with 'label' and an 'on_click' function or a URL.
    - columns: The number of columns to use for the card grid display.
    """
    # Create a grid layout with a specified number of columns
    grid: List[List[Tuple[int, dict]]] = [[] for _ in range(columns)]

    # Distribute cards data into the grid layout
    for idx, card in enumerate(cards_data):
        column_index = idx % columns
        grid[column_index].append((idx, card))

    # Render the grid of cards
    cols = st.columns(columns)
    for col_idx, cards_in_column in enumerate(grid):
        with cols[col_idx]:
            for _card_idx, card in cards_in_column:
                st.subheader(card["title"])
                for item in card.get("body", []):
                    if item["label"]:
                        st.markdown(f"**{item['label']}:** {item['value']}")
                    else:
                        st.markdown(f"{item['value']}")

                    # Card footer with action buttons
                    with mui.CardActions(disableSpacing=True):
                        for _button_idx, button in enumerate(card.get("footer", [])):
                            if "page" in button:
                                # Example button opening a URL
                                with mui.Paper:
                                    button["page"].link()
