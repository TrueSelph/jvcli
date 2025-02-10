"""Render the Jivas Studio page in an iframe."""

import streamlit as st
from streamlit_router import StreamlitRouter

from jvcli.client.app import JIVAS_STUDIO_URL


def render(router: StreamlitRouter) -> None:
    """
    Render the Jivas Studio page in an iframe.

    args:
        router: StreamlitRouter
            The StreamlitRouter instance
    """

    st.components.v1.iframe(JIVAS_STUDIO_URL, width=None, height=800, scrolling=False)
