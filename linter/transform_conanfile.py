
# Class ConanFile doesn't declare all the valid members and functions,
#   some are injected by Conan dynamically to the class.

import textwrap
import astroid
from astroid.builder import AstroidBuilder
from astroid.builder import extract_node
from astroid.inference_tip import inference_tip
from astroid.manager import AstroidManager


def _settings_transform():
    module = AstroidBuilder(AstroidManager()).string_build(
        textwrap.dedent("""
            class Settings(object):
                os = None
                arch = None
                compiler = None
                build_type = None
            """)
    )
    return module['Settings']

def _user_info_build_transform():
    module = AstroidBuilder(AstroidManager()).string_build(
        textwrap.dedent("""
            class UserInfoBuild(defaultdict):
                pass
            """)
    )
    return module['UserInfoBuild']


def register(_):
    pass

def transform_conanfile(node):
    """Transform definition of ConanFile class so dynamic fields are visible to pylint"""

    str_class = astroid.builtin_lookup("str")
    dict_class = astroid.builtin_lookup("dict")
    info_class = astroid.MANAGER.ast_from_module_name("conans.model.info").lookup(
        "ConanInfo")
    build_requires_class = astroid.MANAGER.ast_from_module_name(
        "conans.model.requires").lookup("BuildRequirements")
    tool_requires_class = astroid.MANAGER.ast_from_module_name(
        "conans.model.requires").lookup("ToolRequirements")
    test_requires_class = astroid.MANAGER.ast_from_module_name(
        "conans.model.requires").lookup("TestRequirements")
    python_requires_class = astroid.MANAGER.ast_from_module_name(
        "conans.client.graph.python_requires").lookup("PyRequires")

    dynamic_fields = {
        "conan_data": str_class,
        "build_requires": build_requires_class,
        "test_requires" : test_requires_class,
        "tool_requires": tool_requires_class,
        "info_build": info_class,
        "user_info_build": [_user_info_build_transform()],
        "info": info_class,
        "python_requires": [str_class, python_requires_class],
        "recipe_folder": str_class,
        "settings_build": [_settings_transform()],
        "settings_target": [_settings_transform()],
        "conf": dict_class,
    }
    
    for f, t in dynamic_fields.items():
        node.locals[f] = [i for i in t]


astroid.MANAGER.register_transform(
    astroid.ClassDef, transform_conanfile,
    lambda node: node.qname() == "conans.model.conan_file.ConanFile")


def _looks_like_settings(node: astroid.Attribute) -> bool:
    return node.attrname == "settings"

def infer_settings(node, context):
    return astroid.MANAGER.ast_from_module_name(
        "conans.model.settings").lookup("Settings")[1][0].instantiate_class().infer(context=context)

astroid.MANAGER.register_transform(
    astroid.Attribute,
    inference_tip(infer_settings),
    _looks_like_settings,
)