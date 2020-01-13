# Release Notes

<!-- MarkdownTOC autolink="true" bracket="round" -->

## January 13, 2019 - Introducing The New ConanCenter!

When you visit the new ConanCenter, you’ll notice the search bar prominent on the first page. You can use it to search for any package by name or description, and retrieve a list of results showing the package version and number of downloads. 
You’ll also notice that the new center is focused primarily on package discovery, and meant to help package authors find rich metadata by providing quick access to your Conan packages recipe and configuration information. Each package version has a recipe tab where you can download the recipe as a text file for your project. Package authors can also easily add new packages. Join the [Early Access Program](https://github.com/conan-io/conan-center-index/wiki) on our GitHub repo conan-center-index and make a pull request to recipes. Once approved, those packages are indexed and provided on the new Conan Center UI. 

A few more improvements to the new ConanCenter include:
* A new configurations page UI
* Access to a multitude of configurations for each version of your package
* New Social Media links
* Improved SEO for search and discovery
* All versions and revisions for each package are available in the UI

## Artifactory at its Core

One primary infrastructural change with the new ConanCenter is that packages are now being stored on [JFrog Artifactory](https://conan.io/downloads.html) through an improved process we call the continuous integration system. This process includes verifying new packages from Conan authors added through a pull request on the recipes for the conan-center-index repository on GitHub. This improves and provides more visibility into how packages get into ConanCenter. We’ve opened up this process as part of an [Early Access Program](https://github.com/conan-io/conan-center-index/wiki) which you can join today.
