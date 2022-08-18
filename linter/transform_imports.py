
import astroid
from pylint.lint import PyLinter

"""
Here we are transforming the imports to mimic future Conan v2 release. With
these changes, built-in checks in Pylint will raise with different errors, so
we are modifying the messages to point users in the right direction.
"""


def register(linter: PyLinter):
    msge1101 = linter.msgs_store._messages_definitions["E1101"]
    msge1101.msg += ". Please, check https://github.com/conan-io/conan-center-index/blob/master/docs/v2_linter.md"
    linter.msgs_store.register_message(msge1101)

    msge0611 = linter.msgs_store._messages_definitions["E0611"]
    msge0611.msg += ". Please, check https://github.com/conan-io/conan-center-index/blob/master/docs/v2_linter.md"
    linter.msgs_store.register_message(msge0611)

def transform_tools(module):
    """ Transform import module """
    if 'get' in module.locals:
        del module.locals['get']
    if 'cross_building' in module.locals:
        del module.locals['cross_building']
    if 'rmdir' in module.locals:
        del module.locals['rmdir']
    if 'Version' in module.locals:
        del module.locals['Version']

def transform_errors(module):
    if 'ConanInvalidConfiguration' in module.locals:
        del module.locals['ConanInvalidConfiguration']
    if 'ConanException' in module.locals:
        del module.locals['ConanException']


astroid.MANAGER.register_transform(
    astroid.Module, transform_tools,
    lambda node: node.qname() == "conans.tools")

astroid.MANAGER.register_transform(
    astroid.Module, transform_errors,
    lambda node: node.qname() == "conans.errors")
