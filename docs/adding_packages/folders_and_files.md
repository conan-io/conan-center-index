# Folder and Files Structure

ConanCenterIndex has a specific structure for its recipes, this allows the [build service](../README.md#the-build-service)
to work most efficiently.

<!-- toc -->
## Contents

  * [Recipe File Structure](#recipe-file-structure)
    * [`config.yml`](#configyml)
    * [The _recipe folder_](#the-_recipe-folder_)
      * [`conandata.yml`](#conandatayml)
      * [`test_package`](#test_package)<!-- endToc -->

## Recipe File Structure

Every entry in the `recipes` folder contains all the files required by Conan to create the binaries for all the versions of one library. Those
files don't depend on any other file in the repository (we are not using `python_requires`) and every pull-request can modify only one of those
folders at a time.

This is the canonical structure of one of these folders, where the same `conanfile.py` recipe is suitable to build all the versions of the library:

```txt
.
+-- recipes
|   +-- library_name/
|       +-- config.yml
|       +-- all/
|           +-- conanfile.py
|           +-- conandata.yml
|           +-- patches/
|               +-- 2.1.0-0001-add-missing-string-header-.patch
|           +-- test_package/
|               +-- conanfile.py
|               +-- CMakeLists.txt
|               +-- test_pacakge.cpp
```

If it becomes too complex to maintain the logic for all the versions in a single `conanfile.py`, it is possible to split the folder `all/` into
more folders, dedicated to different versions, each one with its own `conanfile.py` recipe. In any case, those folders should replicate the
same structure.

### `config.yml`

This file lists the versions that should be built along with the corresponding [recipe folder](#the-recipe-folder) that will be used to package the project.

> **Note**: It's strongly preferred to only have one recipe which should be in the `all/` folder.

```yml
versions:
  # It's encouraged to add new versions on the top
  "2.1.0":
    folder: all
  "2.0.0":
    folder: all
```

This simple file has the following format:

* `versions` is a top level dictionary, containing a list of known versions.
* `folder` is a string entry providing the name of the folder, relative to the current directory where the `conanfile.py` that
can package that given folder.

If it's not possible to maintain one recipe for all version, older version maybe moved to a separate folder.

```yml
versions:
  "2.1.0":
    folder: all
  "2.0.0":
    folder: all
  "1.1.1":
    folder: 1.x.x # Older version with different build system and options that are not compatible with newer version
```

### The _recipe folder_

This contains every needed to build packages.

#### `conandata.yml`

This file lists **all the sources** that are needed to build the package. The most common examples are
source code, build scripts, license files. The Conandata is officially documented in [using the conandata.yml](https://docs.conan.io/2/tutorial/creating_packages/handle_sources_in_packages.html#using-the-conandata-yml-file).

For more information about picking source tarballs, adding or removing versions, or what the rules are for patches, continue reading our
[Sources and Patches](sources_and_patches.md) guide.

> **Note**: Under our mission to ensure quality, patches undergo extra scrutiny. **Make sure to review** our
> [modifying sources policy](sources_and_patches.md#policy-about-patching) before making changes.

A detailed breakdown of all the fields can be found in [conandata_yml_format.md](conandata_yml_format.md). We **strongly** recommend adding the
[patch fields](conandata_yml_format.md#patches-fields) to help track where patches come from and what issue they solve.

Inside the `conanfile.py` recipe, this data is available in through the [self.conan_data](https://docs.conan.io/2/reference/conanfile/attributes.html#conan-data) attribute.

#### `test_package`

All the packages in this repository need to be tested before they join ConanCenter. A `test_package` folder with its
corresponding `conanfile.py` and a minimal project to test the package is strictly required. You can read about it in the
[Conan documentation](https://docs.conan.io/2/tutorial/creating_packages/test_conan_packages.html#testing-conan-packages).

The goal for the test package is to make sure the:

* Header files are available
* Libraries are available to link against
* Components are correctly exposed

When providing a test package, please:

* Create a minimal usage for the target project here
* Avoid upstream full examples, or code bigger than 15 lines
* Avoid networking connections
* Avoid background apps or servers
* Avoid GUI apps
* Avoid extra files like images, sounds and other binaries
* The propose is testing the generated artifacts ONLY

Remember that the `test_<package>` recipes should **test the package configuration that has just been generated** for the
_host_ context, otherwise it will fail in cross-building scenarios.
