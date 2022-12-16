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
This is help ensure there are fewer conflicts with other, up to date, recipes that share the same requirements.

### Optional Requirements

If a requirement is conditional, this condition must not depend on build context. Build requirements don't have this constraint.
Add an option, see [naming recommendation](conanfile_attributes.md#recommended-names), and set the default to make the upstream build system.

```py
class ExampleConan(ConanFile):
    options = {
        "with_zlib": [True, False],
    }
    default_options = {
        "with_zlib": True,
    }

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")
```

### Build Requirements

In ConanCenter, we only assume CMake is available, if a project requires a specific tool those can be added as well.
We like to do this with:

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
`validate()` method.

### Handling Requirements Options

Forcing options of dependencies inside a ConanCenter should be avoided, except if it is mandatory for the library to build.
Our general belief is the users input should be the most important; it's unexpected for command line arguements to be over ruled
by specifc recipes.

You need to use the `validate()` method in order to ensure they check after the Conan graph is completely built.

Certain projects are dependant on the configuration (a.k.a options) of a dependency. This can be enforced in a recipe by
accessing the [`options`](https://docs.conan.io/en/latest/reference/conanfile/dependencies.html?highlight=options) feild of
the dependency.

```py
  def validate(self):
      foobar = self.dependencies["foobar"]
      if not foobar.options.enable_feature:
          raise ConanInvalidConfiguration(f"{self.ref} requires foobar/*:enable_feature=True.")
```

### Verifying Dependency Version

Some project requirements need to respect a version constraint, this can be done as follows:

```py
def validate(self):
    foobar = self.dependencies["foobar"]
    if Version(foobar.ref.version) < "1.2":
        raise ConanInvalidConfiguration(f"{self.ref} requires [foobar>=1.2] to build and work.")
```

### Adherence to Build Service

It's very rare we layout "rules", most often it's guidelines, however in order to ensure graph and the package generated are usable
for consumer, we do impose some limits on Conan features to provide a smoother first taste to using Conan.

> **Note**: These are very specific to the ConanCenter being the default remote and may not be relevant to your specifc use case.

* [Version ranges](https://docs.conan.io/en/latest/versioning/version_ranges.html) are not allowed.
* Specify explicit [RREV](https://docs.conan.io/en/latest/versioning/revisions.html) (recipe revision) of dependencies is not allowed.
* Only ConanCenter recipes are allowed in `requires`/`requirements()` and `build_requires`/`build_requirements()`.
* `python_requires` are not allowed.

### Handling "internal" dependencies

Vendoring in library source code should be removed (best effort) to avoid potential ODR violations. If upstream takes care to rename
symbols, it may be acceptable.
