# Adding Packages to ConanCenter

## Join the Early Access Program

The first step in adding packages to ConanCenter is requesting access to the Early Access Program. To enroll in EAP,  please send an email to info@conan.io with the subject [EAP access] or add a comment on this GitHub [issue](https://github.com/conan-io/conan-center-index/issues/4). The EAP was designed to onboard authors to the new process.

With EAP, contribution of packages are now done via pull requests to the recipe found in the Github repository in https://github.com/conan-io/conan-center-index.

The specific steps to add new packages are:
* Fork the [conan-center-index](https://github.com/conan-io/conan-center-index) git repository, and then clone it.
* Create a new folder with the Conan package recipe (conanfile.py)
* Push to GitHub, and submit a pull request.
* Our automated build service will build 100+ different configurations, and provide messages that indicate if there were any issues found during the pull request on GitHub.

When the pull request is reviewed and merged, those packages are published to center.conan.io.

## More Information about Recipes

The [conan-center-index](https://github.com/conan-io/conan-center-index) (this repository) contains recipes for the [conan-center](https://bintray.com/conan/conan-center) repository.

To contribute with a Conan recipe into the `conan-center` repository you can submit a [Pull Request](https://github.com/conan-io/conan-center-index/pulls) to the **master branch** of this repository. The connected **continuous integration system** will generate binary packages automatically for the most common platforms and compilers. See [the Supported Platforms and Configurations page](supported_platforms_and_configurations.md) to know the generated configurations. For a C++ library, the system is currently generating more than 100 binary packages.

> ⚠️ **Note**: This CI service is not a testing service, it is a binary building service for package **releases**. Unit tests shouldn't be built nor ran in recipes by default. Before submitting a PR it is mandatory to run at least a local package creation.

The CI system will also report with messages in the PR any error in the process, even linking to the logs to see more details and debug.

When pull requests are merged, the CI generated package binaries will be uploaded to ConanCenter. These packages won't contain the `@user/channel` part. You will be able to install them specifying only `library_name/version` as a requirement, omitting the `@user/channel` part. (Conan >= 1.21).

Previously existing packages in ConanCenter, with the full reference including `@user/channel` will still be available, but the previous process of “inclusion request” for getting them into Conan-center is now deprecated, and new contributions should follow this guide. Those packages will be gradually contributed to this repo to generate new binaries without the `@user/channel`.

## How to submit a Pull Request

### Before start

Make sure you are using the latest [Conan client](https://conan.io/downloads) version, the recipes might evolve introducing features of the newer Conan releases.


### The recipe folder

Create a new subfolder in the [recipes](https://github.com/conan-io/conan-center-index/tree/master/recipes) folder with the name of the package in lowercase.

e.g:

```
.
+-- recipes
|   +-- zlib
|       +-- 1.2.8
|           +-- conanfile.py
|           +-- test_package
|       +-- 1.2.11
|           +-- conanfile.py
|           +-- test_package
```

### The version folder/s

The system supports to use the same recipe for several versions of the library and also to create different recipes for different versions

- **1 version => 1 recipe**

  When the recipes change significantly between different library versions and reusing the recipe is not worth it, you can create a folder for each version and create inside both the “conanfile.py” and the “test_package” folder:

  ```
  .
  +-- recipes
  |   +-- zlib
  |       +-- 1.2.8
  |           +-- conanfile.py
  |           +-- test_package

  ```


- **N versions => 1 recipe**

   Create a folder named `all` (just a convention) and put both the “conanfile.py” and the “test_package” folder there. With this approach, the “conanfile.py” won’t declare the `version` attribute.

   You will need to create a `config.yml` file to declare the matching between the versions and the folders. e.g:

  ```
  .
  +-- recipes
  |   +-- mylibrary
  |       +-- all
  |           +-- conanfile.py
  |           +-- test_package
          +-- config.yml
  ```

  **config.yml** file

  ```
  versions:
    "1.1.0":
      folder: all
    "1.1.1":
      folder: all
    "1.1.2":
      folder: all
  ```

- **N versions => M recipes**

   This is the same approach as the previous one, you can use one recipe for a range of versions and a different one for another range of versions. Create the `config.yml` file and declare the folder for each version.

### The conanfile.py and `test_package` folder

   In the folder/s created in the previous step, you have to create the `conanfile.py` and a [test_package](https://docs.conan.io/en/latest/creating_packages/getting_started.html#the-test-package-folder) folder.

### The `conandata.yml`

   In the same directory than the `conanfile.py`, create a file named `conandata.yml`. This file has to be used in the recipe to indicate the origins of the source code. It must have an entry for each version, indicating the `URL` for downloading the source code and a checksum.

```
sources:
  "1.1.0":
    url: "https://www.url.org/source/mylib-1.0.0.tar.gz"
    sha256: "8c48baf3babe0d505d16cfc0cf272589c66d3624264098213db0fb00034728e9"
  "1.1.1":
    url: "https://www.url.org/source/mylib-1.0.1.tar.gz"
    sha256: "15b6393c20030aab02c8e2fe0243cb1d1d18062f6c095d67bca91871dc7f324a"
```

You must specify the checksum algorithm `sha256`.
If your sources are on GitHub, you can copy the link of the "Download ZIP" located in the "Clone or download" repository, make sure you are in the correct branch or TAG.

Then in your `conanfile.py` method, it has to be used to download the sources:

```
 def source(self):
     tools.get(**self.conan_data["sources"][self.version])
```



### Test the recipe locally

 The system will use the [conan-center hook](https://github.com/conan-io/hooks.git) to perform some quality checks. You can install the hook running:

```
    $ conan config install https://github.com/conan-io/hooks.git -sf hooks -tf hooks
    $ conan config set hooks.conan-center
```

  The hook will show error messages but the `conan create` won’t fail unless you export the environment variable `CONAN_HOOK_ERROR_LEVEL=40`.

Call `conan create . lib/1.0@` in the folder of the recipe using the profile you want to test.

### Debugging failed builds

   Go to the [Error Knowledge Base](error_knowledge_base.md) page to know more.
