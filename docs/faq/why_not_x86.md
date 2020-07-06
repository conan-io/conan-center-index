## Why not x86 binaries?

As described in the [Supported platforms and configurations](https://github.com/conan-io/conan-center-index/wiki/Supported-Platforms-And-Configurations), only the x86_64 architecture is available for download, the rest must be built from sources. The reasons behind this decision are:

* Few users need different pre-built packages that are not x86_64 packages, this number is less than 10% of total users (data obtained through the download counter from Bintray), and tends to decrease over the years;
* Some OS are putting the x86 as obsolete, examples [macOS](https://developer.apple.com/documentation/macos-release-notes/macos-catalina-10_15-release-notes) and Ubuntu 20.04;
* For security reasons, most companies build their own packages from sources, even if they already have a pre-built version available, which further reduces the need for extra configurations;
* Each recipe results around 130 packages, and this is only for x86_64, but not all packages are used, some settings remain with zero downloads throughout their life. So, imagine adding more settings that will be rarely used, but that will consume more resources as time and storage, this leaves us in an impractical situation.

#### But if there are no packages available, what will the x86 validation look like?

As stated earlier, any increase in the number of configurations will result in an impractical scenario. In addition, more validations require more review time for a recipe, which would increase the time for all PRs, delaying the release of a new package. For these reasons, x86 is not validated by the CCI.

We often receive new fixes and improvements to the recipes already available for x86_64, including help for other architectures like x86 and ARM. In addition, we also receive new cases of bugs, for recipes that do not work on a certain platform, but that are necessary for use, which is important to understand where we should put more effort. So we believe that the best way to maintain and add support for other architectures is through the community.
