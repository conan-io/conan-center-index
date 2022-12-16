# Dependencies

This section outlines all the practices and guidelines for the `requirements()` and `build_requirements()` methods. This includes everything
from "vendored" dependencies to when and how the versions could be changed.

<!-- toc -->
## Contents<!-- endToc -->

## List Dependencies

Since all ConanCenterIndex recipes are to build and/or package projects, they are exclusively done in `conanfiles.py` which offer a few
way to add requirements. The most common way is:

```py
    def requirements(self):
        self.requires("fmt/9.1.0")
```

> **Note**: With Conan 2.0, you'll also need to pay attention to new properties like the `transitive_header` attributed which is
> needed when a project include a dependencies header files in its public headers.

When a project supports a range of version of a dependency, it's generally advised to pick the most recent available in ConanCenter.
This helps ensure there are fewer conflicts with other, up to date, recipes that share the same requirements.

### Optional Requirements

Many projects support enabling certain features but adding dependencies. In ConanCenterIndex this is done by add an option, see
[naming recommendation](conanfile_attributes.md#recommended-names), which is set match the upstream build system by default.

```py
class ExampleConan(ConanFile):
    options = {
        "with_zlib": [True, False], # Possible values
    }
    default_options = {
        "with_zlib": True, # Could match upstream's CMakeLists.txt `option(with_zlib "" ON)`
    }

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")
```

If a dependency was added (or removed) with a release, then the `if` condition could check `self.version`. Another common case is
`self.settings.os` dependant requirements which need to be added for certain plaforms.

### Build Requirements

In ConanCenter we only assume
[CMake is available](../faqs.md#why-recipes-that-use-build-tools-like-cmake-that-have-packages-in-conan-center-do-not-use-it-as-a-build-require-by-default).
If a project requires any other specific tool, those can be added as well. We like to do this with:

```py
    def build_requirements(self):
        self.tool_requires("ninja/1.1.0")
```

## Accessing Dependencies

It's fairly common to need to pass information from a dependency to the project. This is the job of the `generate()` method.
The [`self.dependencies`](https://docs.conan.io/en/latest/reference/conanfile/dependencies.html?highlight=generate) are available
for the case when built-in generators are not available.

Alternatively, a project may depend on a specific configuration of a dependency. This use case is again covered by the
[`self.dependencies`](https://docs.conan.io/en/latest/reference/conanfile/dependencies.html?highlight=validate) within the
`validate()` method. Additionally it's possible to suggest the option's values while the graph is built through `configure()`
this is not guaranteed and not a common practice.

### Handling Requirement's Options

Forcing options of dependencies inside a ConanCenter should be avoided, except if it is mandatory for the library to build.
Our general belief is the users input should be the most important; it's unexpected for command line arguements to be over ruled
by specifc recipes.

You need to use the `validate()` method in order to ensure they check after the Conan graph is completely built.

Certain projects are dependant on the configuration (a.k.a options) of a dependency. This can be enforced in a recipe by
accessing the [`options`](https://docs.conan.io/en/latest/reference/conanfile/dependencies.html?highlight=options) feild of
the dependency.

```py
  def configure(self):
      self.options["foobar"].enable_feature = True # This will still allow users to override this option

  def validate(self):
      if not self.dependencies["foobar"].options.enable_feature:
          raise ConanInvalidConfiguration(f"{self.ref} requires foobar/*:enable_feature=True.")
```

### Verifying Dependency's Version

Some project requirements need to respect a version constraint, this can be done as follows:

```py
def validate(self):
    if Version(self.dependencies["foobar"].ref.version) < "1.2":
        raise ConanInvalidConfiguration(f"{self.ref} requires [foobar>=1.2] to build and work.")
```

### Passing Requirement's info to `build()`

The `self.dependencies` are limtied to `generate()` and `validate()`. This means configuring a projects build scripts
is a touch more complicated when working with unsupported build scripts.

In general, with CMake project, this can be very simple with the `CMakeToolchain`, such as:

```py
    def generate(self):
        tc = CMakeToolchain(self)
        # deps_cpp_info, deps_env_info and deps_user_info are no longer used
        if self.dependencies["dependency"].options.foobar:
            tc.variables["DEPENDENCY_LIBPATH"] = self.dependencies["dependency"].cpp_info.libdirs
```

This pattern can be recreated for less common build system by, generating a script to call configure or  capture the
required values in a YAML files for example.

> **Note**: This needs to be saved to disk because the `conan install` and `conan build` commands can be seperated when
> developing packages so for this reason the `class` may not presists the information. This is a very common workflow,
> even used in ConanCenter in other areas such as testing.

```py
from conan import ConanFile
from conan.tools.files import save, load


class ExampleConan(ConanFile):
    _optional_build_args = []

    @property
    def _optional_build_args_filename(self):
        return os.path.join(self.recipe_folder, self.folders.generators, "build_args.yml")

    def generate(self):
        # This is required as `self.dependencies` is not available in `build()` or `test()`
        if self.dependencies["foobar"].options.with_compression:
            self._optional_build_args.append("--enable-foobar-compression")

        save(self, self._optional_build_args_filename, file)

    def build(self):
        opts_args = load(self, self._optional_build_args_filename)
        # Some magic setup
        self.run(f"./configure.sh {opts_args}")
```

## Adherence to Build Service

It's very rare we layout "rules", most often it's guidelines, however in order to ensure graph and the package generated are usable
for consumer, we do impose some limits on Conan features to provide a smoother first taste to using Conan.

> **Note**: These are very specific to the ConanCenter being the default remote and may not be relevant to your specifc use case.

* [Version ranges](https://docs.conan.io/en/latest/versioning/version_ranges.html) are not allowed.
* Specify explicit [RREV](https://docs.conan.io/en/latest/versioning/revisions.html) (recipe revision) of dependencies is not allowed.
* Only ConanCenter recipes are allowed in `requires`/`requirements()` and `build_requires`/`build_requirements()`.
* `python_requires` are not allowed.

## Handling "internal" dependencies

Vendoring in library source code should be removed (best effort) to avoid potential ODR violations. If upstream takes care to rename
symbols, it may be acceptable.
