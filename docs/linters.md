## Conan Center Index Linters

Some linter configuration files are available in the folder [linter](../linter), which are executed by Github Actions to improve recipe quality.
They consume python scripts which are executed to fit CCI rules. Those scripts use [astroid](https://github.com/PyCQA/astroid) and
[pylint](https://pylint.pycqa.org/en/latest/) classes to parse Conan recipe files and manage their warnings and errors.

The pylint by itselt is not able to find Conan Center Index rules, so astroid is used to iterate over conanfiles content and
validate CCI conditions. Also, pylint uses [rcfile](https://pylint.pycqa.org/en/latest/user_guide/configuration/index.html)
(a configuration file based on [toml](https://toml.io/en/) format) to configure plugins, warnings and errors which should be enabled or disabled.

Also, the Github [code review](https://github.com/features/code-review) is integrated with the pylint output,
parsed by [recipe_linter.json](../linter/recipe_linter.json), then presented to all users on the tab `Files changed`.

Of course, if wanto to run any linter locally, before pushing your code, read [Running the linter locally](v2_linter.md#running-the-linter-locally).


### [Pylint Recipe](../linter/pylintrc_recipe)

This rcfile lists plugins and rules to be executed over all recipes (not test package) and validate them:

- W9006 - conan-import-conanfile: ConanFile should be imported from conan

```python
from conans import ConanFile
```

Should be replaced by:

```python
from conan import Conanfile
```

- E9004 - conan-package-name: Conan package names must be lower-case

The package name is always lower-case, even when the upstream uses another format

```python
def FoobarConanfile(ConanFile):
    name = "foobar"
```

- E9005 - conan-missing-name: Every conan recipe must contain the attribute name

The attribute `name` is always expected. On the other hand, `version` should not be listed.

```python
def BazConanfile(ConanFile):
    name = "baz"
```

#### E9008 - conan-import-errors: Deprecated imports should be replaced by new imports. Read [v2_linter](v2_linter.md)

Regular imports from `conans.tools` are now updated:

```python
from conans import tools
...

tools.rmdir(os.path.join(self.package_folder, "shared"))
```

Should be replaced by specilized tools, prepared for Conan 2.0

```python
from conan.tools.files import rmdir
...

rmdir(self, os.path.join(self.package_folder, "shared"))
```

* E9009 - conan-import-error-conanexception: conans.errors is deprecated and conan.errors should be used instead

```python
from conans.errors import ConanException
```

Should be replaced by:

```python
from conan.errors import ConanException
```

Only the namespace `conans` has been replaced by `conan`.


* E9010 - conan-import-error-conaninvalidconfiguration: conans.errors is deprecated and conan.errors should be used instead

```python
from conans.errors import ConanInvalidConfiguration
```

Should be replaced by:

```python
from conan.errors import ConanInvalidConfiguration
```

Only the namespace `conans` has been replaced by `conan`.

* E9011 - conan-import-tools: Importing conan.tools or conan.tools.xxx.zzz.yyy should be considered as private

Documented on [conanfile.tools](https://docs.conan.io/en/latest/reference/conanfile/tools.html):


It's not allowed to use `tools.xxx` directly:

```python
from conan import tools
...

tools.scm.Version(self.version)
```

Neither sub modules:

```python
from conan.tools.apple.apple import is_apple_os
```

Only modules under `conan.tools` and `conan.tools.xxx` are allowed:

```python
from conan.tools.files import rmdir
from conan.tools import scm
````

### [Pylint Test Package Recipe](../linter/pylintrc_testpackage)

This rcfile lists plugins and rules to be executed over all recipes in test package folders only:

* W9006 - conan-import-conanfile: ConanFile should be imported from conan

```python
from conans import ConanFile
```

Should be replaced by:

```python
from conan import Conanfile
```

* E9007 - conan-test-no-name: Do not add name attribute in test package recipes

The test package is not a package, thus, it should not have a name

```python
def TestPackageConanFile(ConanFile):
    name = "test_package" # Wrong!
```

* E9008 - conan-import-errors: Deprecated imports should be replaced by new imports. Read [v2_linter](v2_linter.md)

Regular imports from `conans.tools` are now updated:

```python
from conans import tools
...

if tools.cross_building(self):
```

Should be replaced by specilized tools, prepared for Conan 2.0

```python
from conan.tools.build import cross_building
...

if cross_building(self):
```

* E9009 - conan-import-error-conanexception: conans.errors is deprecated and conan.errors should be used instead

```python
from conans.errors import ConanException
```

Should be replaced by:

```python
from conan.errors import ConanException
```

Only the namespace `conans` has been replaced by `conan`.


* E9010 - conan-import-error-conaninvalidconfiguration: conans.errors is deprecated and conan.errors should be used instead

```python
from conans.errors import ConanInvalidConfiguration
```

Should be replaced by:

```python
from conan.errors import ConanInvalidConfiguration
```

Only the namespace `conans` has been replaced by `conan`.

* E9011 - conan-import-tools: Importing conan.tools or conan.tools.xxx.zzz.yyy should be considered as private

Documented on [conanfile.tools](https://docs.conan.io/en/latest/reference/conanfile/tools.html):


It's not allowed to use `tools.xxx` directly:

```python
from conan import tools
...

tools.scm.Version(self.version)
```

Neither sub modules:

```python
from conan.tools.apple.apple import is_apple_os
```

Only modules under `conan.tools` and `conan.tools.xxx` are allowed:

```python
from conan.tools.files import rmdir
from conan.tools import scm
````
