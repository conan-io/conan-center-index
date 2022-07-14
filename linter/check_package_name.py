from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
from astroid import nodes, Const, AssignName


class PackageName(BaseChecker):
    """
       All packages must have a lower-case name
    """

    __implements__ = IAstroidChecker

    name = "conan-package-name"
    msgs = {
        "E9004": (
            "Reference name should be all lowercase",
            "conan-bad-name",
            "Use only lower-case on the package name: `name = 'foobar'`."
        ),
        "E9005": (
            "Missing name attribute",
            "conan-missing-name",
            "The member attribute `name` must be declared: `name = 'foobar'`."
        )
    }

    def visit_classdef(self, node: nodes) -> None:
        if node.basenames == ['ConanFile']:
            for attr in node.body:
                children = list(attr.get_children())
                if len(children) == 2 and \
                   isinstance(children[0], AssignName) and \
                   children[0].name == "name" and \
                   isinstance(children[1], Const):
                    value = children[1].as_string()
                    if value.lower() != value:
                        self.add_message("conan-bad-name", node=attr, line=attr.lineno)
                    return
            self.add_message("conan-missing-name", node=node)
