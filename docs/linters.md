## Conan Center Index Linters

Some linter configuration files are available in the folder [linter](../linter), which are executed by Github Actions to improve recipe quality.
They consume python scripts which are executed to fit CCI rules. Those scripts use `astroid` and `pylint` classes.

To run any linter locally, read [Running the linter locally](v2_linter.md#running-the-linter-locally).


#### [Pylint Recipe](../linter/pylintrc_recipe)

This rcfile lists plugins and rules to be executed over all recipes (not test package) and validate them:

- W9006 - conan-import-conanfile: ConanFile should be imported from conan
- E9004 - conan-package-name: Conan package names must be lower-case
- E9005 - conan-missing-name: Every conan recipe must contain the attribute name
- E9008 - conan-import-errors: Deprecated imports should be replaced by new imports. Read [v2_linter](v2_linter.md)
- E9009 - conan-import-error-conanexception: conans.errors is deprecated and conan.errors should be used instead
- E9010 - conan-import-error-conaninvalidconfiguration: conans.errors is deprecated and conan.errors should be used instead
- E9011 - conan-import-tools: Importing conan.tools or conan.tools.xxx.zzz.yyy should be considered as private

#### [Pylint Test Package Recipe](../linter/pylintrc_testpackage)

This rcfile lists plugins and rules to be executed over all recipes in test package folders only:

- W9006 - conan-import-conanfile: ConanFile should be imported from conan
- E9007 - conan-test-no-name: Do not add `name` attribute in test package recipes
- E9008 - conan-import-errors: Deprecated imports should be replaced by new imports. Read [v2_linter](v2_linter.md)
- E9009 - conan-import-error-conanexception: conans.errors is deprecated and conan.errors should be used instead
- E9010 - conan-import-error-conaninvalidconfiguration: conans.errors is deprecated and conan.errors should be used instead
- E9011 - conan-import-tools: Importing conan.tools or conan.tools.xxx.zzz.yyy should be considered as private
