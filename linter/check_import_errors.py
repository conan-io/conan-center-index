
from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
from astroid import nodes, Const, AssignName


class ImportErrorsConanException(BaseChecker):
    """
       Import errors from new 'conan' module
    """

    __implements__ = IAstroidChecker

    name = "conan-import-error-conanexception"
    msgs = {
        "E9008": (
            "Import ConanException from new module: `from conan.errors import ConanException`. Old import is deprecated in Conan v2.",
            "conan-import-error-conanexception",
            "Import ConanException from new module: `from conan.errors import ConanException`. Old import is deprecated in Conan v2.",
        ),
    }

    def visit_importfrom(self, node: nodes.ImportFrom) -> None:
        basename = node.modname
        if basename == 'conans.errors':
            names = [name for name, _ in node.names]
            if 'ConanException' in names:
                self.add_message("conan-import-error-conanexception", node=node)


class ImportErrorsConanInvalidConfiguration(BaseChecker):
    """
       Import errors from new 'conan' module
    """

    __implements__ = IAstroidChecker

    name = "conan-import-error-conaninvalidconfiguration"
    msgs = {
        "E9009": (
            "Import ConanInvalidConfiguration from new module: `from conan.errors import ConanInvalidConfiguration`. Old import is deprecated in Conan v2.",
            "conan-import-error-conaninvalidconfiguration",
            "Import ConanInvalidConfiguration from new module: `from conan.errors import ConanInvalidConfiguration`. Old import is deprecated in Conan v2.",
        ),
    }

    def visit_importfrom(self, node: nodes.ImportFrom) -> None:
        basename = node.modname
        if basename == 'conans.errors':
            names = [name for name, _ in node.names]
            if 'ConanInvalidConfiguration' in names:
                self.add_message("conan-import-error-conaninvalidconfiguration", node=node)

