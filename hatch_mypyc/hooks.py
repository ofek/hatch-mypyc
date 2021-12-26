from hatchling.plugin import hookimpl

from .plugin import MypycBuildHook


@hookimpl
def hatch_register_build_hook():
    return MypycBuildHook
