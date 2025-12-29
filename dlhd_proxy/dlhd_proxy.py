from typing import List

import reflex as rx

import dlhd_proxy.pages
from dlhd_proxy import backend
from dlhd_proxy.components import card, navbar
from dlhd_proxy.step_daddy import Channel


def _search_box() -> rx.Component:
    """Reusable search input for filtering channels."""

    return rx.input(
        rx.input.slot(rx.icon("search")),
        placeholder="Search channels...",
        on_change=IndexState.set_search_query,
        value=IndexState.search_query,
        width="100%",
        max_width="25rem",
        size="3",
    )


def _channel_grid() -> rx.Component:
    """Responsive channel card grid."""

    return rx.flex(
        rx.foreach(
            IndexState.filtered_channels,
            lambda channel: rx.box(
                card(channel),
                width="100%",
                max_width="320px",
                min_width="240px",
                style={"flex": "1 1 260px"},
            ),
        ),
        wrap="wrap",
        justify="center",
        align="stretch",
        spacing=rx.breakpoints(initial="4", sm="6", lg="7"),
        width="100%",
    )


def _desktop_channels() -> rx.Component:
    """Desktop experience loads channels automatically."""

    return rx.desktop_only(
        rx.box(
            rx.cond(
                IndexState.has_channels,
                _channel_grid(),
                rx.center(rx.spinner(), height="50vh"),
            ),
        ),
        on_mount=IndexState.load_channels,
    )


def _mobile_channels() -> rx.Component:
    """Mobile experience uses an explicit load trigger."""

    return rx.mobile_and_tablet(
        rx.cond(
            IndexState.has_channels,
            _channel_grid(),
            rx.button(
                "Load channels...",
                on_click=IndexState.load_channels,
                loading=IndexState.is_loading,
                size="3",
            ),
        ),
    )


class IndexState(rx.State):
    channels: List[Channel] = []
    search_query: str = ""
    is_loading: bool = False

    @rx.var
    def has_channels(self) -> bool:
        return bool(self.channels)

    @rx.var
    def filtered_channels(self) -> List[Channel]:
        query = self.search_query.strip().lower()
        if not query:
            return self.channels
        return [ch for ch in self.channels if query in ch.name.lower()]

    async def load_channels(self):
        """Populate the channel list if it has not been loaded."""

        if self.channels or self.is_loading:
            return

        self.is_loading = True
        try:
            self.channels = backend.get_enabled_channels()
        finally:
            self.is_loading = False


@rx.page("/")
def index() -> rx.Component:
    return rx.box(
        navbar(_search_box()),
        rx.center(
            rx.vstack(
                _desktop_channels(),
                _mobile_channels(),
            ),
            padding="1rem",
            padding_top="10rem",
        ),
    )


app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="red",
    ),
    stylesheets=[
        "/css/styles.css",
    ],
    api_transformer=backend.fastapi_app,
)

app.register_lifespan_task(backend.update_channels)
app.register_lifespan_task(backend.auto_update_guide)
