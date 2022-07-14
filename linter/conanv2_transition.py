"""Pylint plugin for Conan Center Index"""
from pylint.lint import PyLinter
from linter.check_package_name import PackageName
from linter.check_import_conanfile import ImportConanFile


def register(linter: PyLinter) -> None:
    linter.register_checker(PackageName(linter))
    linter.register_checker(ImportConanFile(linter))
