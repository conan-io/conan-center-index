# Dependencies

This section outlines all the practices and guidelines for the `requirements()` and `build_requirements()` methods. This includes everything from "vendored" dependencies to
when and how the versions could be changed.

<!-- toc -->
## Contents

  * [Rules](#rules)<!-- endToc -->

## Rules

* [Version range](https://docs.conan.io/en/latest/versioning/version_ranges.html) is not allowed.
* Specify explicit [RREV](https://docs.conan.io/en/latest/versioning/revisions.html) (recipe revision) of dependencies is not allowed.
* Vendoring in library source code should be removed (best effort) to avoid potential ODR violations. If upstream takes care to rename
  symbols, it may be acceptable.
* Only ConanCenter recipes are allowed in `requires`/`requirements()` and `build_requires`/`build_requirements()`.
* If a requirement is conditional, this condition must not depend on [build context](https://docs.conan.io/en/1.35/devtools/build_requires.html#build-and-host-contexts). Build requirements don't have this constraint.
* Forcing options of dependencies inside a recipe should be avoided, except if it is mandatory for the library - in which case it must
  be enforced through the `validate()` methods.
