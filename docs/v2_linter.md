Linter to help migration to Conan v2
====================================

<!-- toc -->
## Contents

  * [Import ConanFile from `conan`](#import-conanfile-from-conan)
  * [Import tools from `conan`](#import-tools-from-conan)<!-- endToc -->

On our [path to Conan v2](v2_roadmap.md) we are leveraging on custom Pylint rules. This
linter will run for every pull-request that is submitted to the repository and will
raise some warnings and errors that should be addressed in order to migrate the
recipes to Conan v2.

It is important to note that these rules are targetting Conan v2 compatibility layer, their
purpose is to fail for v1 syntax that will be no longer available in v2. Even if the syntax
if perfectly valid in Conan v1, the recipe might fail here because it is not v2-compliant.

> **Note.-** Some of the errored checks might be just plain Python syntax errors, while
> others might be related to the custom rules added by us.

Here you can find some examples of the extra rules we are adding:

## Import ConanFile from `conan`

The module `conans` is deprecated in Conan v2. Now all the imports should be done from
module `conan`:

```python
from conan import ConanFile
```

## Import tools from `conan`

All v2-compatible tools are available in module `conan.tools` under different submodules. Recipes
should start to import their tools from this new module. Some of the new tools accept new
argument, please, check the [Conan documentation](https://docs.conan.io/en/latest/reference/conanfile/tools.html).

Here is a list of different imports and their new equivalent (note that the interface for most of this functions changed, see their respective link to the documentation):

| **Conan v1** | **Conan v2** |
|---|---|
| conans.tools.get | [conan.tools.files.get](https://docs.conan.io/en/latest/reference/conanfile/tools/files/downloads.html#conan-tools-files-get) |
| conans.tools.cross_building | [conan.tools.build.cross_building](https://docs.conan.io/en/latest/reference/conanfile/tools/build.html#conan-tools-build-cross-building) |
| conans.tools.rmdir | [conan.tools.files.rmdir](https://docs.conan.io/en/latest/reference/conanfile/tools/files/basic.html#conan-tools-files-rmdir) |
| conans.errors.ConanInvalidConfiguration | [conan.errors.ConanInvalidConfiguration](https://docs.conan.io/en/latest/migrating_to_2.0/recipes.html#migrating-the-recipes) |
| conans.errors.ConanException | [conan.errors.ConanException](https://docs.conan.io/en/latest/migrating_to_2.0/recipes.html#migrating-the-recipes) |


# Disable linter for `test_v1_*/conanfile.py`

Using the pattern `test_v1_*/conanfile.py` you can write a test that will be executed using only Conan v1,
you probably don't want v2-migration linter to check this file, as it will likely contain syntax that is
specific to Conan v1.

To skip the file you just need to add the following comment to the file and `pylint` will skip it:

**`test_v1_*/conanfile.py`**
```python
# pylint: skip-file
from conans import ConanFile, CMake, tools
...
```
