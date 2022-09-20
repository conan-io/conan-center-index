# Linter to help migration to Conan v2

<!-- toc -->
## Contents

  * [Import ConanFile from `conan`](#import-conanfile-from-conan)
  * [Import tools from `conan`](#import-tools-from-conan)
  * [Disable linter for a specific conanfile](#disable-linter-for-a-specific-conanfile)
  * [Running the linter locally](#running-the-linter-locally)<!-- endToc -->

On our [path to Conan v2](v2_roadmap.md) we are leveraging on custom Pylint rules. This
linter will run for every pull-request that is submitted to the repository and will
raise some warnings and errors that should be addressed in order to migrate the
recipes to Conan v2.

It is important to note that these rules are targeting Conan v2 compatibility layer, their
purpose is to fail for v1 syntax that will be no longer available in v2. Even if the syntax
if perfectly valid in Conan v1, the recipe might fail here because it is not v2-compliant.

> **Note** Some of the errored checks might be just plain Python syntax errors, while
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

| **Conan v1** | **Conan v2** | **Required Conan Version** |
|---|---|---|
| conans.tools.get | [conan.tools.files.get](https://docs.conan.io/en/latest/reference/conanfile/tools/files/downloads.html#conan-tools-files-get) | 1.41.0 |
| conans.tools.download | [conan.tools.files.download](https://docs.conan.io/en/latest/reference/conanfile/tools/files/downloads.html#conan-tools-files-download) | 1.41.0 |
| conans.tools.rmdir | [conan.tools.files.rmdir](https://docs.conan.io/en/latest/reference/conanfile/tools/files/basic.html#conan-tools-files-rmdir) | 1.47.0 |
| conans.tools.patch | [conan.tools.files.patch](https://docs.conan.io/en/latest/reference/tools.html#tools-patch) | 1.35.0 |
| conans.tools.remove_files_by_mask | [conan.tools.files.rm](https://docs.conan.io/en/latest/reference/conanfile/tools/files/basic.html#conan-tools-files-rm) | 1.50.0 |
| conans.copy | [conan.tools.files.copy](https://docs.conan.io/en/latest/reference/conanfile/tools/files/basic.html#conan-tools-files-copy) | 1.46.0 |
| conans.tools.load | [conan.tools.files.load](https://docs.conan.io/en/latest/reference/conanfile/tools/files/basic.html#conan-tools-files-load) | 1.35.0 |
| conans.tools.save | [conan.tools.files.save](https://docs.conan.io/en/latest/reference/conanfile/tools/files/basic.html#conan-tools-files-save) | 1.35.0 |
| conans.tools.rename | [conan.tools.files.rename](https://docs.conan.io/en/latest/reference/conanfile/tools/files/basic.html#conan-tools-files-rename) | 1.37.0 |
| conans.tools.replace_in_file | [conan.tools.files.replace_in_file](https://docs.conan.io/en/latest/reference/conanfile/tools/files/basic.html#conan-tools-files-replace-in-file) | 1.46.0 |
| conans.tools.mkdir | [conan.tools.files.mkdir](https://docs.conan.io/en/latest/reference/conanfile/tools/files/basic.html#conan-tools-files-mkdir) | 1.35.0 |
| conans.tools.chdir | [conan.tools.files.chdir](https://docs.conan.io/en/latest/reference/conanfile/tools/files/basic.html#conan-tools-files-chdir) | 1.40.0 |
| conans.tools.unzip | [conan.tools.files.unzip](https://docs.conan.io/en/latest/reference/conanfile/tools/files/basic.html#conan-tools-files-unzip) | 1.46.0 |
| conans.tools.collect_libs | [conan.tools.files.collect_libs](https://docs.conan.io/en/latest/reference/conanfile/tools/files/basic.html#conan-tools-files-collect-libs) | 1.46.0 |
| conans.tools.Version | [conan.tools.scm.Version](https://docs.conan.io/en/latest/reference/conanfile/tools/scm/other.html#version) | 1.46.0 |
| conans.tools.sha256sum | [conan.tools.files.check_sha256](https://docs.conan.io/en/latest/reference/conanfile/tools/files/checksum.html#conan-tools-files-check-sha256) | 1.46.0 |
| conans.tools.unix_path | [conan.tools.microsoft.unix_path](https://docs.conan.io/en/latest/reference/conanfile/tools/microsoft.html#conan-tools-microsoft-unix-path) | 1.47.0 |
| conans.tools.is_apple_os | [conan.tools.apple.is_apple_os](https://docs.conan.io/en/latest/reference/conanfile/tools/apple.html#is-apple-os) | 1.51.3 |
| conans.tools.cpu_count | [conan.tools.build.build_jobs](https://docs.conan.io/en/latest/reference/conanfile/tools/build.html#conan-tools-build-build-jobs) | 1.43.0 |
| conans.tools.check_min_cppstd | [conan.tools.build.check_min_cppstd](https://docs.conan.io/en/latest/reference/conanfile/tools/build.html#conan-tools-build-check-min-cppstd) | 1.50.0 |
| conans.tools.cross_building | [conan.tools.build.cross_building](https://docs.conan.io/en/latest/reference/conanfile/tools/build.html#conan-tools-build-cross-building) | 1.46.0 |
| conans.errors.ConanInvalidConfiguration | [conan.errors.ConanInvalidConfiguration](https://docs.conan.io/en/latest/migrating_to_2.0/recipes.html#migrating-the-recipes) | 1.47.0 |
| conans.errors.ConanException | [conan.errors.ConanException](https://docs.conan.io/en/latest/migrating_to_2.0/recipes.html#migrating-the-recipes) | 1.47.0 |

---

## Running the linter locally

It is possible to run the linter locally the same way it is being run [using Github actions](../.github/workflows/linter-conan-v2.yml):

 * (Recommended) Use a dedicated Python virtualenv.
 * Ensure you have required tools installed: `conan` and `pylint` (better to uses fixed versions)

   ```
   pip install conan~=1.0 pylint==2.14
   ```

 * Set environment variable `PYTHONPATH` to the root of the repository

   ```
   export PYTHONPATH=your/path/conan-center-index
   ```

  * Now you just need to execute the `pylint` commands:

    ```
    # Lint a recipe:
    pylint --rcfile=linter/pylintrc_recipe recipes/boost/all/conanfile.py

    # Lint the test_package
    pylint --rcfile=linter/pylintrc_testpackage recipes/boost/all/test_package/conanfile.py
    ```
