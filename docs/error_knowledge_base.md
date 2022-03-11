# Errors from the conan-center hook (KB-Hxxx)


#### **<a name="KB-H001">#KB-H001</a>: "DEPRECATED GLOBAL CPPSTD"**

`Conan > 1.15` deprecated the usage of the global ``cppstd`` setting in favor of ``compiler.cppstd``. As a subsetting of the compiler, it shouldn't be declared in the `conanfile.py`.

#### **<a name="KB-H002">#KB-H002</a>: "REFERENCE LOWERCASE"**

The package names in conan-center have to be lowercase. e.g: ``zlib/1.2.8``

#### **<a name="KB-H003">#KB-H003</a>: "RECIPE METADATA"**

The recipe has to declare the following fields: [url](https://docs.conan.io/en/latest/reference/conanfile/attributes.html#url), [license](https://docs.conan.io/en/latest/reference/conanfile/attributes.html#license), [description](https://docs.conan.io/en/latest/reference/conanfile/attributes.html#description) and [homepage](https://docs.conan.io/en/latest/reference/conanfile/attributes.html#homepage). Also we recommend adding [topics](https://docs.conan.io/en/latest/reference/conanfile/attributes.html#topics).

#### **<a name="KB-H005">#KB-H005</a>: "HEADER_ONLY, NO COPY SOURCE"**

If the recipe calls `self.info.header_only()` in the `package_id()` method and doesn't declare settings, it should use the [no_copy_source](https://docs.conan.io/en/latest/reference/conanfile/attributes.html#no-copy-source) attribute to avoid unnecessary copies of the source code.

#### **<a name="KB-H006">#KB-H006</a>: "FPIC OPTION"**

The recipe is not for a header-only library and should have an `fPIC` option:

```python
class SomeRecipe(ConanFile):
    ...

    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}
```

#### **<a name="KB-H007">#KB-H007</a>: "FPIC MANAGEMENT"**

The recipe declares `fPIC` but doesn't remove the option for Windows (where it doesn't make sense).

```python
class SomeRecipe(ConanFile):
    ...

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
```

Or, a package is built as `shared` library and `fPIC` is declared. The option `fPIC` should be removed:

```python
class SomeRecipe(ConanFile):
    ...

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
```

Here we use `configure()` method, because user options are loaded after `config_options()` only.


#### **<a name="KB-H008">#KB-H008</a>: "VERSION RANGES"**

It is not allowed to use version ranges for the recipes in Conan center, where the dependency graph should be deterministic.


#### **<a name="KB-H009">#KB-H009</a>: "RECIPE FOLDER SIZE"**

The recipe folder (including the `test_package` folder) cannot exceed 256KB.

#### **<a name="KB-H010">#KB-H010</a>: "IMMUTABLE SOURCES"**

Create a file `conandata.yml` in the recipe folder containing the source code origins:

**_recipes/lib/1.2.0/conandata.yml_**:

```yaml
sources:
  1.2.0:
    url: "http://downloads.sourceforge.net/project/mylib/1.2.0/sources.tar.gz"
    sha256: "36658cb768a54c1d4dec43c3116c27ed893e88b02ecfcb44f2166f9c0b7f2a0d"
```

Then in the recipe, you can access the data to download the URL and validate the checksum doing:

```python
class SomeRecipe(ConanFile):
    ...

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
```

#### **<a name="KB-H011">#KB-H011</a>: "LIBCXX MANAGEMENT"**

If the library is detected as a pure C library (sources doesn't conatain any file with the following extensions: ["cc", "cpp", "cxx", "c++m", "cppm", "cxxm", "h++", "hh", "hxx", "hpp"]) then it has to remove the `compiler.libcxx` subsetting, because the cpp standard library shouldn't affect the binary ID:

```python
class SomeRecipe(ConanFile):
    ...

    def configure(self):
        del self.settings.compiler.libcxx
```

#### **<a name="KB-H012">#KB-H012</a>: "PACKAGE LICENSE"**

The binary packages should contain a folder named `licenses` containing the contents (library, tool, etc) license/s.

#### **<a name="KB-H013">#KB-H013</a>: "DEFAULT PACKAGE LAYOUT"**

The binary packages shouldn't contain any other files or folder except the following: `["lib", "bin", "include", "res", "licenses"]`. If you are packaging an application put all the contents inside the `bin` folder.


#### **<a name="KB-H014">#KB-H014</a>: "MATCHING CONFIGURATION"**

The binary package contains some file that not corresponds to the configuration of the package, for example, binary libraries for a header-only library, a DLL file when the `settings.os != Windows` and so on. The error message will contain information about the offending file.

#### **<a name="KB-H015">#KB-H015</a>: "SHARED ARTIFACTS"**

The binary package is shared (self.options.shared == True) but there is no `dll`, `so` or `dylib` files inside the package.

#### **<a name="KB-H016">#KB-H016</a>: "CMAKE-MODULES-CONFIG-FILES"**

The binary package cannot contain module or config CMake files ("Find*.cmake", "*Config.cmake",                                                                   "*-config.cmake").

The package shouldn't contain specific build-system files to inform to the consumers how to link with it.
In order to make sure that the package will be consumed with any build-system, conan-center repository encourages to declare a `def package_info(self)` method with all the needed information about the package.

The consumers of the package will be able to consume the packages using a specific [generators](https://docs.conan.io/en/latest/using_packages/conanfile_txt.html#generators) for the build system they use.

#### **<a name="KB-H017">#KB-H017</a>: "PDB FILES NOT ALLOWED"**

Because of the big size of the PDB files and the issues using them changing the original folders, the PDB files are not allowed to be packaged.

#### **<a name="KB-H018">#KB-H018</a>: "LIBTOOL FILES PRESENCE"**

Packaging libtool files (*.la) instead of library files (*.a) is not allowed.

#### **<a name="KB-H0119">#KB-H019</a>: "CMAKE FILE NOT IN BUILD FOLDERS"**

Some file with `*.cmake` extension has been found in a folder not declared in `cpp_info.builddirs`.
It is only allowed to put build files in `builddirs` because the generators might be able to include them when needed, but only if they are located in well known paths.

#### **<a name="KB-H020">#KB-H020</a>: "PC-FILES"**

For the same reasons explained at [KB-H016](#KB-H016) it is not allowed to package `*.pc` files.

#### **<a name="KB-H021">#KB-H021</a>: "MS RUNTIME FILES"**

For the legal reasons, and in order to reduce the size of packages, it's not allowed to package Microsoft Visual Studio runtime libraries, such as `msvcr80.dll`, `msvcp80.dll`, `vcruntime140.dll` and so on.

#### **<a name="KB-H022">#KB-H022</a>: "CPPSTD MANAGEMENT"**

If the library is detected as a pure C library (sources doesn't conatain any file with the following extensions: ["cc", "cpp", "cxx", "c++m", "cppm", "cxxm", "h++", "hh", "hxx", "hpp"]) then it has to remove the compiler.cppstd subsetting, because the cpp standard library shouldn't affect the binary ID:

```python
class SomeRecipe(ConanFile):
    ...

    def configure(self):
        del self.settings.compiler.cppstd
```

#### **<a name="KB-H023">#KB-H023</a>: "EXPORT LICENSE"**

A recipe should not export any license file, as all recipes are under the same license type (in the root of this repo).

```python
class SomeRecipe(ConanFile):
    ...

    exports = "LICENSE.md" # not allowed
```

There is a complete explanation in the [FAQ](faqs.md#should-recipes-export-a-recipes-license).

#### **<a name="KB-H024">#KB-H024</a>: "TEST PACKAGE FOLDER"**

The [test_package](https://docs.conan.io/en/latest/creating_packages/getting_started.html#the-test-package-folder) folder is required for every recipe in Conan Center Index.

```
. conanfile.py
. test_package
  |- conanfile.py
```

#### **<a name="KB-H025">#KB-H025</a>: "META LINES"**

The following metadata lines (and similiar) are not allowed in recipes:

- [Shebang](https://en.wikipedia.org/wiki/Shebang_(Unix)) to specify Python version:

```python
#!/usr/bin/env python  # not allowed
#!/usr/local/bin/python  # not allowed

class SomeRecipe(ConanFile):
    ...
```

- [Vim](https://www.vim.org/) configuration:

```python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 # not allowed

class SomeRecipe(ConanFile):
    ...
```

- Encoding:

```python
# -*- coding: utf-8 -*-  # not allowed
# coding=utf-16          # not allowed

class SomeRecipe(ConanFile):
    ...
```

#### **<a name="KB-H027">#KB-H027</a>: "CONAN CENTER INDEX URL"**

The attribute `url` should point to the address where the recipe is located.
The current Conan Center Index address is https://github.com/conan-io/conan-center-index

#### **<a name="KB-H028">#KB-H028</a>: "CMAKE MINIMUM VERSION"**

All CMake files added to recipe package should contain a minimal version (Not necessarily 2.8.11, it can be any version) available in the file:

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 2.8.11)
project(conanwrapper)

...
```

#### **<a name="KB-H029">#KB-H029</a>: "TEST PACKAGE - RUN ENVIRONMENT"**

The [RunEnvironment()](https://docs.conan.io/en/latest/reference/build_helpers/run_environment.html#runenvironment) build helper is no longer needed in the *test_package/conanfile.py*. It has been integrated by [run_environment](https://docs.conan.io/en/latest/devtools/running_packages.html#running-from-packages) parameter.

```python
# test_package/conanfile.py
class TestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def test(self):
        self.run("bin/test", run_environment=True)
```

#### **<a name="KB-H030">#KB-H030</a>: "CONANDATA.YML FORMAT"**

The structure of the *conandata.yml* file should follow this schema:

```yml
sources:
  "1.69.0":
    url: "url1.69.0"
    sha256: "sha1.69.0"
  "1.70.0":
    url: "url1.70.0"
    sha256: "sha1.70.0"
patches:
  "1.70.0":
    - patch_file: "001-1.70.0.patch"
      base_path: "source_subfolder/1.70.0"
    - url: "https://fake_url.com/custom.patch"
      sha256: "sha_custom"
      base_path: "source_subfolder"
  "1.71.0":
    - patch_file: "001-1.71.0.patch"
      base_path: "source_subfolder/1.71.0"
```

#### **<a name="KB-H031">#KB-H031</a>: "CONANDATA.YML REDUCE"**

This hook re-creates the information of the *conandata.yml* file, discarding the fields not relevant to the version of the package exported. This avoids creating new recipe revisions for every new change introduced in the file.
Any additional field in the YAML file will raise an error.
#### **<a name="KB-H032">#KB-H032</a>: "SYSTEM REQUIREMENTS"**

System requires can be used as an option when a Conan package is not available the same package can be installer system package manager. However, it can cause  reproducibility problems, since the package may vary according the distribution or OS. Conan is not able to track its metadata, so that, installing system packages by recipe is not allowed.

#### **<a name="KB-H034">#KB-H034</a>: "TEST PACKAGE - NO IMPORTS()"**

The method [imports](https://docs.conan.io/en/latest/reference/conanfile/methods.html#imports) helps the test package stage copying all dynamic libraries and special resources. However, the [run_environment](https://docs.conan.io/en/latest/reference/conanfile/other.html#running-commands) parameter, used when running commands, is able to solve all paths to the dynamic libraries installed in your cache.

#### **<a name="KB-H037">#KB-H037</a>: "NO AUTHOR"**

Since the entire community is maintaining all CCI recipes, putting just one name in a recipe is unfair, putting all names is unmanageable. All authors can be found in the Git logs.

#### **<a name="KB-H040">#KB-H040</a>: "NO TARGET NAME"**

According the Conan issue [#6269](https://github.com/conan-io/conan/issues/6269), the attribute `cpp_info.name` should be avoided for Conan Center Index in favor of `cpp_info.names["cmake_find_package"]` and `cpp_info.names["cmake_find_package_multi"]`.

#### **<a name="KB-H041">#KB-H041</a>: "NO FINAL ENDLINE"**

Source files should end with a final endline.
This avoids potential warnings/errors like `no new line at the end of file`.

#### **<a name="KB-H044">#KB-H044</a>: "NO REQUIRES.ADD()"**

Both `self.requires.add()` and `self.build_requires.add()` have been deprecated in favor of `self.requires()` and `self.build_requires()` which were introduced on Conan 1.x. Both `add()` were introduced during Conan 0.x and since Conan 1.23 they no longer follow the original behavior.

#### **<a name="KB-H045">#KB-H045</a>: "DELETE OPTIONS"**

The method `self.options.remove()` was introduced in Conan 0.x, however, Conan 1.x brings a more pythonic way for removing options from your recipe: `del self.options.<option_name>`

#### **<a name="KB-H046">#KB-H046</a>: "CMAKE VERBOSE MAKEFILE"**

The CMake definition CMAKE_VERBOSE_MAKEFILE helps for debugging when developing, however, for regular CI build, it increases the log size and it's only required when problems occur and need to be verified.

#### **<a name="KB-H048">#KB-H048</a>: "CMAKE VERSION REQUIRED"**

The file test_package/CMakeLists.txt should require CMake 3.1 by default: `cmake_minimum_required(VERSION 3.1)`. The CMake wrapper file can require CMake 2.8, because Conan recipe and the test package are totally separated. However, if `CMAKE_CXX_STANDARD` or `CXX_STANDARD` is explicit, CMake 3.1 is mandatory.

#### **<a name="KB-H049">#KB-H049</a>: "CMAKE WINDOWS EXPORT ALL SYMBOLS"**

The CMakeLists.txt definitions [CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS](https://cmake.org/cmake/help/v3.4/variable/CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS.html) and [WINDOWS_EXPORT_ALL_SYMBOLS](https://cmake.org/cmake/help/v3.4/prop_tgt/WINDOWS_EXPORT_ALL_SYMBOLS.html) are available since CMake 3.4 only. Any previous version will ignore it.

#### **<a name="KB-H050">#KB-H050</a>: "DEFAULT SHARED OPTION VALUE"**

By default, all packages should be built as static library (the option ``shared`` is ``False`` in ``default_options``). However, some projects can be restricted to shared library only, for those cases, open a new [issue](https://github.com/conan-io/hooks/issues) to include the package name in the allowlist.

#### **<a name="KB-H051">#KB-H051</a>: "DEFAULT OPTIONS AS DICTIONARY"**

The attribue `default_options` should be a dictionary, for example `default_options = {'shared': False, 'fPIC': True}`.

#### **<a name="KB-H052">#KB-H052</a>: "CONFIG.YML HAS NEW VERSION"**

It's important to have new library version defined in both `config.yml` and `conandata.yml`, otherwise newly added version will not be checked and built by CI and will not be available for download.

#### **<a name="KB-H053">#KB-H053</a>: "PRIVATE IMPORTS"**

The recipe imports private Conan API, this is strongly discouraged - private imports are subjects to breaking changes. Avoid usage of private APIs, request to publically expose needed methods, if necessary.

#### **<a name="KB-H054">#KB-H054</a>: "LIBRARY DOES NOT EXIST"**

Libraries which are listed on [Components](https://docs.conan.io/en/latest/creating_packages/package_information.html#package-information-components) must be present in `libdirs`. Check if the library name is correct, or if a library is only generated for a specific platform.

#### **<a name="KB-H055">#KB-H055</a>: "SINGLE REQUIRES"**

Do not use `requirements()` and `self.requires` together in the same recipe.
The duality creates a heterogeneous way of solving dependencies, making it difficult to review and susceptible to prone errors.

#### **<a name="KB-H056">#KB-H056</a>: "LICENSE PUBLIC DOMAIN"**

Public Domain is not a license by itself, but consists of all the creative work to which no exclusive intellectual property rights apply.
If a project is under Public Domain and there is no license listed, the [Unlicense](https://spdx.org/licenses/Unlicense) should be used.

#### **<a name="KB-H057">#KB-H057</a>: "TOOLS RENAME"**

The [rename()](https://docs.conan.io/en/latest/reference/conanfile/tools/files.html#conan-tools-rename) method will be the standard for Conan 2.0, and
also, it uses [robocopy](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/robocopy), which is safer on Windows.

#### **<a name="KB-H058">#KB-H058</a>: "ILLEGAL CHARACTERS"**

Windows [naming conventions](https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file#naming-conventions) and [reserved](https://en.wikipedia.org/wiki/Filename#Reserved_characters_and_words) characters must be avoided for file naming, otherwise the will not be supported on Windows.

#### **<a name="KB-H059">#KB-H059</a>: "CLASS NAME"**

Generic class names can cause review confusion. To keep a better naming, it should use `<Package>Conan`.

#### **<a name="KB-H060">#KB-H060</a>: "NO CRLF"**

Files with CRLF as endline can cause CI errors when building a package, due the conversion to LF and false detection from CI as changed file.
The .gitattribute file lists which files should be converted to LF when commit. However, if you want to enforce it in your local copy, you may run:

    > git config --local core.autocrlf false
    > git config --local core.eol lf

The `core.autocrlf` disabled means that git will not convert from CRLF to LF on commit. The `core.eol` sets the specific line ending to be used for every commit.

#### **<a name="KB-H062">#KB-H062</a>: "TOOLS CROSS BUILDING"**

Replace all occurrences of `tools.cross_building(self.settings)` with `tools.cross_building(self)`.
When cross building, conan needs to compare `self.settings` and `self.settings_build`, which are attributes of `self`.

#### **<a name="KB-H064">#KB-H064</a>: "INVALID TOPICS"**

An invalid topic has been detected. Remove or rename it.

# Deprecated errors

The following errors from the hooks are deprecated and no longer reported:

#### **<a name="KB-H047">#KB-H047</a>: "NO ASCII CHARACTERS"**

According to PEP [263](https://www.python.org/dev/peps/pep-0263/), Unicode literals should only appear in Python code if the encoding is declared on one of the first two lines of the source file. Without such a declaration, any Unicode literal will cause a syntax error for Python 2 interpreters.

