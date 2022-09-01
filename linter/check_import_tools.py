import re
from email.mime import base
from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
from astroid import nodes, Const, AssignName


class ImportTools(BaseChecker):
    """
       Import tools following pattern 'from conan.tools.xxxx import yyyyy'
    """

    __implements__ = IAstroidChecker

    name = "conan-import-tools"
    msgs = {
        "E9011": (
            "Import tools following pattern 'from conan.tools.xxxx import yyyyy' (https://docs.conan.io/en/latest/reference/conanfile/tools.html).",
            "conan-import-tools",
            "Import tools following pattern 'from conan.tools.xxxx import yyyyy' (https://docs.conan.io/en/latest/reference/conanfile/tools.html).",
        ),
    }

    def visit_importfrom(self, node: nodes.ImportFrom) -> None:
        basename = node.modname
        names = [name for name, _ in node.names]
        if basename == 'conan' and 'tools' in names:
            self.add_message("conan-import-tools", node=node)
        elif basename == 'conan.tools':
            self.add_message("conan-import-tools", node=node)
        elif re.match(r'conan\.tools\.[^.]+\..+', basename):
            self.add_message("conan-import-tools", node=node)
