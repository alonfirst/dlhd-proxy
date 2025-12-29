import reflex as rx
from reflex.components.component import NoSSRComponent


class MediaPlayer(NoSSRComponent):
    library = "/public/player"
    lib_dependencies: list[str] = ["@vidstack/react@next"]
    tag = "VidstackPlayer"                 # name Reflex will use in JSX
    alias = "VidstackPlayerImport"         # name used for the static import
    is_default = True                      # <-- THIS is the key for default exports
    title: rx.Var[str]
    src: rx.Var[str]
    autoplay: bool = True
