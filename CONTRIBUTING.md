# Contributing to Conan Center Index

The following summarizes the process for contributing to the CCI (Conan Center Index) project.

<!-- toc -->
## Contents

  * [Community](#community)
  * [Dev-flow & Pull Requests](#dev-flow--pull-requests)
  * [Issues](#issues)<!-- endToc -->

## Community

Conan Center Index is an Open Source MIT licensed project.
Conan Center Index is developed by the Conan maintainers and a great community of contributors.

## Dev-flow & Pull Requests

CCI follows the ["GitFlow"](https://datasift.github.io/gitflow/IntroducingGitFlow.html) branching model.
Issues are triaged and categorized mainly by type (package request, bug...) and priority (high, medium...) using GitHub
 labels.

To contribute follow the next steps:

1. Comment in the corresponding issue that you want to contribute the package/fix proposed. If there is no open issue, we strongly suggest
   to open one to gather feedback.
2. Check the [how_to_add_packages.md](docs/how_to_add_packages.md) if are
   contributing for a new package.
3. Fork the [CCI repository](https://github.com/conan-io/conan-center-index) and create a `package/xxx` branch from the `master` branch and develop
   your fix/packages as discussed in previous step.
4. Try to keep your branch updated with the `master` branch to avoid conflicts.
5. Add the text (besides other comments): "fixes #IssueNumber" in the body of the PR, referring to the issue of step 1.

The ``conan-io`` organization maintainers will review and help with the packaging.

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

We use the following tags to control the status of the issues:

- **infrastructure**: Waiting on tools or services belonging to the infra.
- **library request**: Request a new package to be created.
- **question**: Further information is requested .
- **upstream update**: Bump a new package version.
- **conan.io/center**: Issues and features related to Web UI .
