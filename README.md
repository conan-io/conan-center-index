<img src="assets/JFrogConanCenter.png" width="600"/>

This is the source index of recipes of the [ConanCenter](https://conan.io/center) package repository.

This repository includes a Continuous Integration system that will build automatically the Conan packages for the recipes submitted via
[Pull Request](https://github.com/conan-io/conan-center-index/pulls).


### You can learn how to contribute new recipes and how this build service works in [the wiki of the project](https://github.com/conan-io/conan-center-index/wiki).


### Reporting Issues

You can open issues in the [issue tracker](https://github.com/conan-io/conan-center-index/issues) to:

- Report **bugs/issues** in a package: 
    - Use the `[package]` tag in the title of the issue to help identifying them. 
    - If you detect any issue or missing feature in a package, for example, a build failure or a recipe that not support a specific configuration.
    - Specify the name and version (`zlib/1.2.11`) and any relevant details about the fail configuration: Applied profile, building machine...
- Request a **new library** to be added:
    - Use the `[request]` label to search the library in the issue tracker in case the it was already requested.
    - If not, use the same `[request]` tag in the title of the issue to help identifying them.
    - Indicate the name and the version of the library you would like to have in the repository. Also links to the project's website,
      source download/repository and in general any relevant information that helps creating a recipe for it.
- Report **a failure** in the CI system:
    - If you open a Pull Request and get an unexpected error you might comment in the failing PR.
    - If the service or repository is down or failing, use the `[service]` tag in the title of a new issue to help identifying them.

If your issue is not appropriate for a public discussion, please contact us via e-mail at `info@conan.io`. Thanks!
