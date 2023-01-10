# Contributing to Conan Center Index

The following summarizes the process for contributing to the CCI (Conan Center Index) project.

<!-- toc -->
## Contents

  * [Community](#community)
  * [Dev-flow & Pull Requests](#dev-flow--pull-requests)
  * [Issues](#issues)<!-- endToc -->

## Community

ConanCenterIndex is an Open Source MIT licensed project; it is developed by the Conan maintainers and a great community of contributors.

## Dev-flow & Pull Requests

CCI follows the ["GitFlow"](https://datasift.github.io/gitflow/IntroducingGitFlow.html) branching model.
Issues are triaged and categorized mainly by type (package request, bug...) and priority (high, medium...) using GitHub
labels.

To contribute follow the next steps:

1. Comment in the corresponding issue that you want to contribute the package/fix proposed. If there is no open issue, we strongly suggest
   opening one to gather feedback.
2. Make sure to [request access](docs/adding_packages/README.md#request-access) and be aware there is a [CLA](docs/CONTRIBUTOR_LICENSE_AGREEMENT.md).
3. Get setup by following the [Developing Recipes](docs/developing_recipes_locally.md) guide and learn the basic commands.
4. Check the [How To Add Packages](docs/adding_packages/README.md) page for the break down of ConanCenterIndex specific conventions and practices.
5. In your fork create a `package/xxx` branch from the `master` branch and develop
   your fix/packages as discussed in previous step.
6. [Submit a pull request](docs/adding_packages/README.md#submitting-a-package) once you are ready. This can be when you
   got everything working or even if you need help. Add the text to the issue body (besides other comments): "fixes #IssueNumber"
   in the body of the PR, referring to the issue of step 1.

The Conan Community works hard to review all the pull requests and provided assistance where need.
The [Review Process](docs/review_process.md) is partially automated with the help of @conan-center-index-bot :rocket:

## Issues

If you think you found a bug in CCI or in a recipe, open an issue indicating the following:

- Explain the Conan version, Operating System, compiler and any other tool that could be related to the issue.
- Explain, as detailed as possible, how to reproduce the issue. Use git repository to contain code/recipes to reproduce issues, or a snippet.
- Include the expected behavior as well as what actually happened.
- Provide output captures (as text).
- Feel free to attach a screenshot or video illustrating the issue if you think it will be helpful.

For any suggestion, feature request or question open an issue indicating the following:

- Questions and support requests are always welcome.
- Use the [question] or [suggestion] tags in the title (provided by github issues templates).
- Try to explain the motivation, what are you trying to do, what is the pain it tries to solve.
- What do you expect from CCI.

We use the following tags to control the status of the issues and pull requests, you can learn more in [Labels](docs/labels.md) document
which details the important one and their roles.
