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
2. Make sure to [request access](docs/adding_packages/README.md#request-access) and be aware there is a [contributor licenses agreement](https://cla-assistant.io/conan-io/conan-center-index).
3. Get setup by following the [Developing Recipes](docs/developing_recipes_locally.md) guide and learn the basic commands.
4. Check the [How To Add Packages](docs/adding_packages/README.md) page for the break down of ConanCenterIndex specific conventions and practices.
5. In your fork create a `package/xxx` branch from the `master` branch and develop
   your fix/packages as discussed in previous step.
6. [Submit a pull request](docs/adding_packages/README.md#submitting-a-package) once you are ready. This can be when you
   got everything working or even if you need help. Add the text to the issue body (besides other comments): "fixes #IssueNumber"
   in the body of the PR, referring to the issue of step 1.

The Conan Community works hard to review all the pull requests and provide assistance where need.
The [Review Process](docs/review_process.md) is partially automated with the help of @conan-center-index-bot :rocket:

## Pull Request scope

Pull requests should propose changes to a single recipe only. If you believe modifications
to multiple recipes are necessary, we kindly ask that you open an issue first to discuss
the best approach with the maintainer team.

Please ensure that pull requests have a **single**, clear objective that is evident to
reviewers, with all proposed changes directly supporting that goal. Please refrain from
including unrelated modifications, even if they appear minor or trivial.

As the Conan client continues to evolve, we recognize that recipe conventions may change
over time, much like in programming languages themselves. However, please be aware that it
is not a goal in Conan Center to update all recipes to align with the latest conventions,
as this would be an ongoing task that would consume a significant part of our resources.
Changes of this kind will only be considered if they present tangible benefits to the
recipe consumers -such as bug fixes or new features-, and are clearly justified in the
pull request description. Our team will strive to upgrade recipes to the latest
conventions as resources permit. Thank you for your understanding and cooperation.

Please keep in mind that the review team is tasked with assessing a high volume of pull
requests at any given time. To maintain an agile review process, and in accordance with
our previous
[announcement](https://github.com/conan-io/conan-center-index/discussions/25461), we
kindly ask that PRs refrain from performing large-scale refactorings to eliminate Conan
1.x compatibility, or refactoring recipe logic, unless the changes are directly related to
the PR objective (bugfix or feature). Pull requests that include changes unrelated to the
PR objective will not be reviewed and may be closed.

## Pull Request limits

The pull request workflow is constrained by our available resources, including the number
of team reviewers and CI capacity. Given Conan Center’s large user base and its role
within the Software Supply Chain, each pull request undergoes the same validation process
prior to merging. Our objective is to minimize disruption for our users and prioritize
security.

To help manage the workload of the reviewing team and our CI resources, while ensuring
that all contributors have an equitable opportunity for their pull requests to be
reviewed, please note the following limits:

- Pull requests from new contributors, or from trusted contributors after a period of
  inactivity, need to be visually inspected by a team member before starting the CI job.
- For trusted contributors, pull requests will automatically be checked by CI up to a
  maximum of 30 open pull requests by the same contributor. Beyond this limit, CI runs
  will require manual approval by the team.
- Contributors are limited to a maximum of 50 open pull requests at any given time.
  Additional pull requests will be closed or not reviewed until the limit is reduced. 

We thank you for playing a part in prioritizing your own pull requests before opening them
for review and CI checks. For use cases that may require modifying multiple recipes or
extensive changes across the repository, we encourage you to first open an issue. This
allows us to assess user interest, determine if the feature aligns with the project’s
goals, and discuss potential implementation strategies. This helps us prioritize focusing
on the impact proposed features have on the wider Conan Center community.

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
