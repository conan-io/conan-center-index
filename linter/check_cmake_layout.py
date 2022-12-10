from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
from astroid import nodes


class CmakeLayout(BaseChecker):
    """
    Do not add src_folder to cmake_layout
    """

    __implements__ = IAstroidChecker

    name = "conan-cmake-layout"
    msgs = {
        "W9012": (
            "cmake_layout should omit `src_folder` argument",
            "conan-cmake-layout-src-folder",
            "Omit `src_folder` from cmake_layout.",
        )
    }

    def visit_call(self, node: nodes.Call) -> None:
        if (
            isinstance(node.func, nodes.Name)
            and node.func.name == "cmake_layout"
            and "src_folder" in (kw.arg for kw in node.keywords)
        ):
            self.add_message(
                "conan-cmake-layout-src-folder", node=node, line=node.lineno
            )
