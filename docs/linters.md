# ConanCenterIndex Linters

Some linter configuration files are available in the folder [linter](../linter), which are executed by Github Actions
and are displayed during [code review](https://github.com/features/code-review) as annotations, to improve recipe quality.
They consume python scripts which are executed to fit CCI rules. Those scripts use [astroid](https://github.com/PyCQA/astroid)
and [pylint](https://pylint.pycqa.org/en/latest/) classes to parse Conan recipe files and manage their warnings and errors.

Pylint by itself is not able to find ConanCenterIndex rules, so astroid is used to iterate over a conanfile's content and
validate CCI requirements. Pylint uses an [rcfile](https://pylint.pycqa.org/en/latest/user_guide/configuration/index.html)
to configure plugins, warnings and errors which should be enabled or disabled.

<!-- toc -->
## Contents

  * [Understanding the different linters](#understanding-the-different-linters)
  * [Running the linters locally](#running-the-linters-locally)
  * [Pylint configuration files](#pylint-configuration-files)<!-- endToc -->

## Understanding the different linters

There's a three classes of linters currently in place for ConanCenterIndex

- ConanCenter Hook - these are responsible for validating the structure of the recipes and packages.
- Pylint Linter - these are used to ensure the code quality and conventions of a recipes (i.e `conanfile.py`)
- Yaml Checks - stylistic guidance and schema validation check for support files and best practices

## Running the linters locally

Check the [Developing Recipes](developing_recipes_locally.md) for more information on each of the three linters.

## Pylint configuration files

- [Pylint Recipe](../linter/pylintrc_recipe): This `rcfile` lists plugins and rules to be executed over all recipes (not test package) and validate them.
- [Pylint Test Package Recipe](../linter/pylintrc_testpackage): This `rcfile` lists plugins and rules to be executed over all recipes in test package folders only:
