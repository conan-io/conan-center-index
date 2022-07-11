
from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
from astroid import nodes, Const, AssignName


class ImportConanFile(BaseChecker):
    """
       Import ConanFile from new 'conan' module
    """

    __implements__ = IAstroidChecker

    name = "conan-import-conanfile"
    msgs = {
        "W9006": (
            "Import ConanFile from new module: `from conan import ConanFile`. Old import is deprecated in Conan v2.",
            "conan-import-conanfile",
            "Import ConanFile from new module: `from conan import ConanFile`. Old import is deprecated in Conan v2.",
        ),
    }

    #def visit_import(self, node: nodes.Import) -> None:
    #    names = [name for name, _ in node.names]
    #    for name in names:
    #        self.add_message("conan-import-conanfile", args=["lol", ], node=node)

    def visit_importfrom(self, node: nodes.ImportFrom) -> None:
        basename = node.modname
        if basename == 'conans':
            names = [name for name, _ in node.names]
            if 'ConanFile' in names:
                self.add_message("conan-import-conanfile", node=node)
