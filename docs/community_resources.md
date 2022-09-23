# Community Resources

This is a curated list of various bots and helpful tools that aim to making approaching Conan-Center-Index and contributing easier.

<!-- toc -->
## Contents

  * [Social Media and More](#social-media-and-more)
  * [Bots](#bots)
  * [Tools](#tools)<!-- endToc -->

## Social Media and More

The community is very active on the [Cpplang's Slack channel](https://cpplang.slack.com/archives/C41CWV9HA), it's a great place to get help.

## Bots

- [Updatable Recipes](https://github.com/qchateau/conan-center-bot): Automatically scans available recipes and checked for new upstream releases and tests one configuration
  - The results can be found here: https://qchateau.github.io/conan-center-bot/#/updatable
- [Conflicting Pull Requests](https://github.com/ericLemanissier/conan-center-conflicting-prs): Checks all the open pull requests for those which edit the same
recipe files and posts a message.
  - The results can be found here: https://ericlemanissier.github.io/conan-center-conflicting-prs/
- [Pending Review](https://github.com/prince-chrismc/conan-center-index-pending-review)
  - The results can be found here: https://prince-chrismc.github.io/conan-center-index-pending-review/
- [System Package Checks](https://github.com/bincrafters/system-packages-checks): Builds automatically all `system` versions of recipes merged on CCI
and being pull requested on a selection of Linux distributions and FreeBSD
  - The results can be found here: https://bincrafters.github.io/system-packages-checks/

## Tools

- [FreeBSD Testing](https://github.com/ericLemanissier/conan-center-index/tree/freebsd): Detects pull requests with `FreeBSD` in the description and runs a test for
one configuration on that platform
  - The results can be found here: https://github.com/ericLemanissier/conan-center-index/actions?query=workflow%3ACI
- [Bincrafters Conventions](https://github.com/bincrafters/bincrafters-conventions): Automatically updates Conan recipes to the latest conventions and rules
