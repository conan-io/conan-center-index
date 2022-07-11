
# Class ConanFile doesn't declare all the valid members and functions,
#   some are injected by Conan dynamically to the class.

import textwrap
import astroid
from astroid.builder import AstroidBuilder
from astroid.manager import AstroidManager


def register(_):
    pass

def transform_tools(module):
    """ Transform import module """
    if 'cross_building' in module.locals:
        del module.locals['cross_building']


astroid.MANAGER.register_transform(
    astroid.Module, transform_tools,
    lambda node: node.qname() == "conans.tools")
