"""Pylint plugin for Conan Center Index"""
from pylint.lint import PyLinter
from linter.package_name import PackageName


def register(linter: PyLinter) -> None:
    linter.register_checker(PackageName(linter))
