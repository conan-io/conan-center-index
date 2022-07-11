
import astroid

def register(_):
    pass

def transform_tools(module):
    """ Transform import module """
    if 'cross_building' in module.locals:
        del module.locals['cross_building']


astroid.MANAGER.register_transform(
    astroid.Module, transform_tools,
    lambda node: node.qname() == "conans.tools")
