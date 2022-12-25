from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
from astroid import nodes, Const, AssignName


class NoPackageName(BaseChecker):
    """
       Conanfile used for testing a package should NOT provide a name
    """

    __implements__ = IAstroidChecker

    name = "conan-test-package-name"
    msgs = {
        "E9007": (
            "No 'name' attribute in test_package conanfile",
            "conan-test-no-name",
            "No 'name' attribute in test_package conanfile."
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
                    self.add_message("conan-test-no-name", node=attr, line=attr.lineno)
