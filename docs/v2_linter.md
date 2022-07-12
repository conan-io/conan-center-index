Linter to help migration to Conan v2
====================================

On our [path to Conan v2](v2_roadmap.md) we are leveraging on custom Pylint rules. This
linter will run for every pull-request that is submitted to the repository and will
raise some warnings and errors that should be addressed in order to migrate the
recipes to Conan v2.

It is important to note that these rules are targetting Conan v2 compatibility layer, their
purpose is to fail for v1 syntax that will be no longer available in v2. Even if the syntax
if perfectly valid in Conan v1, the recipe might fail here because it is not v2-complaint.

Here you can find some examples of these rules:

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

For example, the `cross_building` tool now should be used like:

```python
from conan.tools.build import cross_building

...
class Recipe(ConanFile):

    def test(self):
        if not cross_building(self):
            pass
```
