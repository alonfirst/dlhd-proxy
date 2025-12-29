from dataclasses import dataclass
from typing import Iterable

import reflex as rx
from rxconfig import config


@dataclass(frozen=True, slots=True)
class NavLink:
    text: str
    icon: str
    url: str
    external: bool = False
    new_tab: bool = False


NAV_LINKS: tuple[NavLink, ...] = (
    NavLink("Schedule", "calendar-sync", "/schedule"),
    NavLink("Channels", "list-checks", "/channels"),
    NavLink("Refresh", "refresh-cw", "/refresh"),
    NavLink("playlist.m3u8", "file-down", "/playlist"),
    NavLink("guide.xml", "file-text", "/guide.xml", True),
    NavLink("Logs", "bug", "/logs", True),
    NavLink("Github", "github", "https://github.com/eribbey/dlhd-proxy", True, True),
)


def _link_target(link: NavLink) -> str | None:
    if link.new_tab:
        return "_blank"
    if link.external:
        return "_self"
    return None


def _brand() -> rx.Component:
    title = config.app_name.replace("_", "-")
    return rx.vstack(
        rx.text(title, size="8", weight="bold"),
        rx.box(background_color="#fa5252", width="100%", padding="2.5px"),
        align_items="center",
        gap="0",
        cursor="pointer",
        on_click=rx.redirect("/"),
    )


def _link_row(links: Iterable[NavLink]) -> rx.Component:
    return rx.hstack(
        *[
            rx.link(
                rx.hstack(
                    rx.icon(link.icon, color="white"),
                    rx.text(link.text, size="4", weight="medium", color="white"),
                ),
                href=link.url,
                is_external=link.external,
                target=_link_target(link),
            )
            for link in links
        ],
        spacing="6",
    )


def _menu_items(links: Iterable[NavLink]) -> rx.Component:
    return rx.menu.content(
        *[
            rx.link(
                rx.hstack(
                    rx.icon(link.icon, size=24, color="white"),
                    rx.text(link.text, size="3", weight="medium", color="white"),
                ),
                href=link.url,
                is_external=link.external,
                target=_link_target(link),
                padding="0.5em",
            )
            for link in links
        ]
    )


def navbar(search: rx.Component | None = None) -> rx.Component:
    return rx.box(
        rx.card(
            rx.desktop_only(
                rx.hstack(
                    _brand(),
                    rx.cond(
                        search,
                        search,
                        rx.text(
                            "Watch ",
                            rx.code("live"),
                            " TV channels",
                            align="center",
                            size="4",
                            padding="5px",
                        ),
                    ),
                    _link_row(NAV_LINKS),
                    justify=rx.breakpoints(initial="between"),
                    align_items="center",
                ),
            ),
            rx.mobile_and_tablet(
                rx.vstack(
                    rx.hstack(
                        _brand(),
                        rx.tablet_only(rx.cond(search, search, rx.fragment())),
                        rx.menu.root(
                            rx.menu.trigger(rx.icon("menu", size=30)),
                            _menu_items(NAV_LINKS),
                            justify="end",
                        ),
                        justify=rx.breakpoints(initial="between"),
                        align_items="center",
                        width="100%",
                    ),
                    rx.cond(
                        search,
                        rx.mobile_only(rx.box(search, width="100%"), width="100%"),
                        rx.fragment(),
                    ),
                ),
            ),
            padding="1em",
            width="100%",
        ),
        padding="1rem",
        position="fixed",
        top="0px",
        z_index="2",
        width="100%",
    )
