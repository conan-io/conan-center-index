"""

Pylint plugin/rules for test_package folder in Conan Center Index

"""

from pylint.lint import PyLinter
from linter.check_import_conanfile import ImportConanFile
from linter.check_no_test_package_name import NoPackageName


def register(linter: PyLinter) -> None:
    linter.register_checker(NoPackageName(linter))
    linter.register_checker(ImportConanFile(linter))
