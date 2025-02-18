"""Renders the analytics page of the JVCLI client."""

import calendar
import datetime
import os

import pandas as pd
import requests
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from streamlit_javascript import st_javascript
from streamlit_router import StreamlitRouter

from jvcli.client.lib.utils import get_user_info

JIVAS_URL = os.environ.get("JIVAS_URL", "http://localhost:8000")


def render(router: StreamlitRouter) -> None:
    """Render the analytics page."""
    ctx = get_user_info()

    st.header("Analytics", divider=True)
    today = datetime.date.today()
    last_day = calendar.monthrange(today.year, today.month)[1]

    date_range = st.date_input(
        "Period",
        (
            datetime.date(today.year, today.month, 1),
            datetime.date(today.year, today.month, last_day),
        ),
    )

    (start_date, end_date) = date_range

    # rerender_metrics = render_metrics()
    col1, col2, col3 = st.columns(3)
    timezone = st_javascript(
        """await (async () => {
                const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                console.log(userTimezone)
                return userTimezone
    })().then(returnValue => returnValue)"""
    )

    try:
        selected_agent = st.session_state.get("selected_agent")
        if selected_agent and end_date > start_date:
            interactions_chart(
                token=ctx["token"],
                agent_id=selected_agent["id"],
                start_date=start_date,
                end_date=end_date,
                metric_col=col1,
                timezone=timezone,
            )
            users_chart(
                token=ctx["token"],
                agent_id=selected_agent["id"],
                start_date=start_date,
                end_date=end_date,
                metric_col=col2,
                timezone=timezone,
            )
            channels_chart(
                token=ctx["token"],
                agent_id=selected_agent["id"],
                start_date=start_date,
                end_date=end_date,
                metric_col=col3,
                timezone=timezone,
            )
        else:
            st.text("Invalid date range")
    except Exception as e:
        st.text("Unable to render charts")
        print(e)


def interactions_chart(
    start_date: datetime.date,
    end_date: datetime.date,
    agent_id: str,
    token: str,
    metric_col: DeltaGenerator,
    timezone: str,
) -> None:
    """Render the interactions chart."""
    url = f"{JIVAS_URL}/walker/get_interactions_by_date"

    with st.container(border=True):
        st.subheader("Interactions by Date")
        response = requests.post(
            url=url,
            json={
                "agent_id": agent_id,
                "reporting": True,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "timezone": timezone,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == 200:
            if response_data := response.json():
                chart_data = pd.DataFrame(
                    data=response_data["reports"][0]["data"],
                )
                st.line_chart(chart_data, x="date", y="count")
                total = response_data["reports"][0]["total"]
                metric_col.metric("Interactions", total)


def users_chart(
    start_date: datetime.date,
    end_date: datetime.date,
    agent_id: str,
    token: str,
    metric_col: DeltaGenerator,
    timezone: str,
) -> None:
    """Render the users chart."""
    url = f"{JIVAS_URL}/walker/get_users_by_date"
    with st.container(border=True):
        st.subheader("Users by Date")
        response = requests.post(
            url=url,
            json={
                "agent_id": agent_id,
                "reporting": True,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "timezone": timezone,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == 200:
            if response_data := response.json():
                chart_data = pd.DataFrame(
                    data=response_data["reports"][0]["data"],
                )
                st.line_chart(chart_data, x="date", y="count")
                total = response_data["reports"][0]["total"]
                metric_col.metric("Users", total)


def channels_chart(
    start_date: datetime.date,
    end_date: datetime.date,
    agent_id: str,
    token: str,
    metric_col: DeltaGenerator,
    timezone: str,
) -> None:
    """Render the channels chart."""
    url = f"{JIVAS_URL}/walker/get_channels_by_date"
    with st.container(border=True):
        st.subheader("Channels by Date")
        response = requests.post(
            url=url,
            json={
                "agent_id": agent_id,
                "reporting": True,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "timezone": timezone,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == 200:
            if response_data := response.json():
                chart_data = pd.DataFrame(
                    data=response_data["reports"][0]["data"],
                )
                st.line_chart(chart_data, x="date", y="count")
                total = response_data["reports"][0]["total"]
                metric_col.metric("Channels", total)
