# Folder and Files Structure

ConanCenterIndex has a specific structure for its recipes, this allows the [build service](../README.md#the-build-service)
to work most efficiently.

<!-- toc -->
## Contents

  * [Recipe File Structure](#recipe-file-structure)
    * [`config.yml`](#configyml)
    * [The _recipe folder_](#the-_recipe-folder_)
      * [`conandata.yml`](#conandatayml)
      * [`conanfile.py`](#conanfilepy)
      * [`test_package`](#test_package)<!-- endToc -->

## Recipe File Structure

Every entry in the `recipes` folder contains all the files required by Conan to create the binaries for all the versions of one library. Those
files don't depend on any other file in the repository (we are not using `python_requires`) and every pull-request can modify only one of those
folders at a time.

This is the canonical structure of one of these folders, where the same `conanfile.py` recipe is suitable to build all the versions of the library:

> **Note**: For updating the structure during the [v2 migration](../v2_migration.md) see the [test package](test_packages.md#cmake-targets) document.

```txt
.
+-- recipes
|   +-- library_name/
|       +-- config.yml
|       +-- all/
|           +-- conanfile.py
|           +-- conandata.yml
|           +-- patches/
|               +-- add-missing-string-header-2.1.0.patch
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
source code, build scripts, license files.

The file is organized into two sections, `"sources"` and `"patches"`, each one of them contains the files that are required
for each version of the library. Resources which need to be downloaded are listed under `"source"` should include a checksum
to validate that they do not change. This helps to ensure the build is reproducible at a later point in time. Often
modifications are required for a variety of reasons, which ones are associated to which version are listed under the `"patches"`.

```yml
sources:
  "9.0.0":
    url: "https://github.com/fmtlib/fmt/archive/9.0.0.tar.gz"
    sha256: "9a1e0e9e843a356d65c7604e2c8bf9402b50fe294c355de0095ebd42fb9bd2c5"
```

For more information about picking source tarballs, adding or removing versions, or what the rules are for patches, continue reading our
[Sources and Patches](sources_and_patches.md) guide.

> **Note**: Under our mission to ensure quality, patches undergo extra scrutiny. **Make sure to review** our
> [modifying sources policy](sources_and_patches.md#policy-about-patching) before making changes.

A detailed breakdown of all the fields can be found in [conandata_yml_format.md](conandata_yml_format.md). We **strongly** recommend adding the
[patch fields](conandata_yml_format.md#patches-fields) to help track where patches come from and what issue they solve.

Inside the `conanfile.py` recipe, this data is available in a `self.conan_data` attribute that can be used as follows:

```py
def source(self):
    get(self, **self.conan_data["sources"][self.version], strip_root=True)
```

See the [Export Patches](sources_and_patches.md#exporting-patches) and [Applying Patches](sources_and_patches.md#applying-patches)
for more use cases and examples.

#### `conanfile.py`

This file is the recipe, it contains the logic to build the libraries from source for all the configurations.
It's the single most important part of writing a package. Every `conanfile.py` should be accompanied by at least one
[folder to test the generated packages](#test_package).

Each recipe should derive the `ConanFile` class and implement key attributes and methods.

* Basic attributes and conversions can be found in [`ConanFile` attributes](conanfile_attributes.md)
* Some of the key methods are outlined in this document and will link to more details

```python
from conan import ConanFile

class FmtConan(ConanFile):
    name = "fmt"
    homepage = "https://github.com/fmtlib/fmt"
    # ...
```

When a package needs other packages those can be include with the `requirements()` method.

```python
    def requirements(self):
        self.require("fmt/9.0.0")
```

For more information see the [Dependencies](dependencies.md) documentation.

For compiled libraries, the `build()` method is used along side the [build helpers](https://docs.conan.io/1/reference/build_helpers.html).
This allows you to use the official build script from a project, see [build and package](build_and_package.md) instructions.

```python
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
```

Most of the projects with build scripts support installing the important files. Avoid installing documentation or examples.

```python
    def package(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
```

For some projects, you will need to manually copy files.
Here's an example for a header only library:

```python
    def package(self):
        copy(self, "*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
```

#### `test_package`

All the packages in this repository need to be tested before they join ConanCenter. A `test_package` folder with its
corresponding `conanfile.py` and a minimal project to test the package is strictly required. You can read about it in the
[Conan documentation](https://docs.conan.io/1/creating_packages/getting_started.html) and learn about ConanCenterIndex
specific conventions in [test package](test_packages.md) section.

The goal for the test package is to make sure the

* header files are available
* libraries are available to link against
* components are correctly exposed

> **Note** It's required to verify that the old generators are not broken. You can do so by using the pattern, see
> [KB-H073](../error_knowledge_base.md#kb-h078) for details.

Remember that the `test_<package>` recipes should **test the package configuration that has just been generated** for the
_host_ context, otherwise it will fail in cross-building scenarios.
