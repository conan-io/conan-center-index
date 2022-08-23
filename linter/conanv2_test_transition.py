"""

Pylint plugin/rules for test_package folder in Conan Center Index

"""

from pylint.lint import PyLinter
from linter.check_import_conanfile import ImportConanFile
from linter.check_no_test_package_name import NoPackageName
from linter.check_import_errors import ImportErrorsConanException, ImportErrorsConanInvalidConfiguration, ImportErrors


def register(linter: PyLinter) -> None:
    linter.register_checker(NoPackageName(linter))
    linter.register_checker(ImportConanFile(linter))
    linter.register_checker(ImportErrors(linter))
    linter.register_checker(ImportErrorsConanException(linter))
    linter.register_checker(ImportErrorsConanInvalidConfiguration(linter))
