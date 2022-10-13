
# Class ConanFile doesn't declare all the valid members and functions,
#   some are injected by Conan dynamically to the class.

import textwrap
import astroid
from astroid.builder import AstroidBuilder
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
        "conans.client.graph.graph_manager").lookup("_RecipeBuildRequires")
    file_copier_class = astroid.MANAGER.ast_from_module_name(
        "conans.client.file_copier").lookup("FileCopier")
    file_importer_class = astroid.MANAGER.ast_from_module_name(
        "conans.client.importer").lookup("_FileImporter")
    python_requires_class = astroid.MANAGER.ast_from_module_name(
        "conans.client.graph.python_requires").lookup("PyRequires")

    dynamic_fields = {
        "conan_data": str_class,
        "build_requires": build_requires_class,
        "tool_requires": build_requires_class,
        "info_build": info_class,
        "user_info_build": [_user_info_build_transform()],
        "info": info_class,
        "copy": file_copier_class,
        "copy_deps": file_importer_class,
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
