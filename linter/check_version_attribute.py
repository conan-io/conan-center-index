from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
from astroid import nodes, Const, AssignName


class VersionAttribute(BaseChecker):
    """
       All packages should not enforce a specific version in the recipe
    """

    __implements__ = IAstroidChecker

    name = "conan-attr-version"
    msgs = {
        "E9014": (
            "Recipe should not contain version attribute",
            "conan-forced-version",
            "Do not enforce a specific version in your recipe. Keep it generic for any version."
        ),
    }

    def visit_classdef(self, node: nodes) -> None:
        if node.basenames == ['ConanFile']:
            for attr in node.body:
                children = list(attr.get_children())
                if len(children) == 2 and \
                   isinstance(children[0], AssignName) and \
                   children[0].name == "version" and \
                   isinstance(children[1], Const):
                    value = children[1].as_string().replace('"', "").replace("'", "")
                    if value and value != "system":
                        self.add_message("conan-forced-version", node=attr, line=attr.lineno)
                    return
