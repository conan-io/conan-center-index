
# Class ConanFile doesn't declare all the valid members and functions,
#   some are injected by Conan dynamically to the class.

import astroid


def register(_):
    pass

def transform_conanfile(node):
    """Transform definition of ConanFile class so dynamic fields are visible to pylint"""

    str_class = astroid.builtin_lookup("str")
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
        "info_build": info_class,
        "info": info_class,
        "copy": file_copier_class,
        "copy_deps": file_importer_class,
        "python_requires": [str_class, python_requires_class],
        "recipe_folder": str_class,
    }

    for f, t in dynamic_fields.items():
        node.locals[f] = [i for i in t]


astroid.MANAGER.register_transform(
    astroid.ClassDef, transform_conanfile,
    lambda node: node.qname() == "conans.model.conan_file.ConanFile")
