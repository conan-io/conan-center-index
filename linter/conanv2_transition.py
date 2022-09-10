"""

Pylint plugin/rules for conanfiles in Conan Center Index

"""

from pylint.lint import PyLinter
from linter.check_package_name import PackageName
from linter.check_import_conanfile import ImportConanFile
from linter.check_import_errors import ImportErrorsConanException, ImportErrorsConanInvalidConfiguration, ImportErrors
from linter.check_import_tools import ImportTools


def register(linter: PyLinter) -> None:
    linter.register_checker(PackageName(linter))
    linter.register_checker(ImportConanFile(linter))
    linter.register_checker(ImportErrors(linter))
    linter.register_checker(ImportErrorsConanException(linter))
    linter.register_checker(ImportErrorsConanInvalidConfiguration(linter))
    linter.register_checker(ImportTools(linter))
