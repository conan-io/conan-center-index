from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
from astroid import nodes


class LayoutSrcFolder(BaseChecker):
    """
    Ensure `src_folder=src` when using built-in layouts
    """

    __implements__ = IAstroidChecker

    name = "conan-layout-src-folder"
    msgs = {
        "E9012": (
            "cmake_layout should set `src_folder` to src",
            "conan-cmake-layout-src-folder",
            "Setting the `src_folder` for layouts will help keep an organized and clean workspace when developing recipes locally. The extra folder will help ensure there are no collisions between the upstream sources and recipe's exports - which also extends to what happens in the cache when creating packages",
        )
    }

    def visit_call(self, node: nodes.Call) -> None:
        if not isinstance(node.func, nodes.Name):
            return

        if node.func.name in ["cmake_layout", "vs_layout", "basic_layout"]:
            for kw in node.keywords:
                if kw.arg == 'src_folder':
                    if not kw.value or kw.value.as_string().strip('"\'') != 'src':
                        self.add_message("conan-cmake-layout-src-folder", node=node, line=node.lineno)
                    break
            else:
                self.add_message("conan-cmake-layout-src-folder", node=node, line=node.lineno)
