# Procedure for adding a new VTK version:

* Add new version number to config.yml

* Download the source manually
  For official releases,
  the link is always https://www.vtk.org/files/release/x.y/VTK-x.y.z.tar.gz

* Generate sha256 hash:
  sha256sum VTK-x.y.z.tar.gz

* Add new version, link and sha256 to conandata.yml

* Extract tarball
  tar xf VTK-x.y.z.tar.gz

* Extract module information from source
  ./gather_modules_from_src.py VTK-x.y.z > modules-x.y.z.json
  Add any new unexpected headers to the gather_modules_from_src.py script (around line 82 and 100)
  You need to add code in two places.
  I wanted this to gather all the information possible, and I feel it is important to check
  that the recipe does not need further modifications due to new information in the modules.
 * For single-value pieces of information, copy the pattern from 'library_name'
   Note that 'CONDITION' can handle data on the same line as the header, copy that if required.
 * For multiple-value pieces of information, copy the pattern from 'groups'
 * For true/false pieces of information, copy the pattern from 'wrap_exclude'

* (For now) adjust `def init(self)` and change `HACK_VERSION` to the new version.
  This is required as init() needs the version number before conan can provide it.

* Try `conan create`.  If VTK has added more external dependencies, then there will be
  errors related to "not providing SOMEPACKAGE.cmake"
  Check if conan CCI has this in its repository.
  It is often easier to check the github CCI repo and look through the folders for possible names.

* Errors may also be something like "Required package 'kissfft' not in component 'requires'
  This can happen when a vendored package was built by VTK, but also provided by conan.
  In the case of kissfft, we have to patch to force VTK to use it.
  Else, drop kissfft as a conan requirement and use the vendored version.
  I'm patching to try and use all conan inputs.


# Example adding a new external module

For this example, 9.3.0 added FastFloat and requested version 3.9.0
Conan CCI happens to have this library, so we will try to use conan's version rather than the vendored version.
Check the file contents in:
VTK-x.y.z/ThirdParty/PACKAGE/vtkPACKAGE/README.kitware.md
See if there are any fixes mentioned, apart from the changes VTK makes to vendor the library under vtk's namespace.

In this case, it only mentions namespaces and build integration.

Check the existance of this PACKAGE in the generated file modules-x.y.z.json.
It was named VTK::PACKAGE (ie VTK::fast_float)

Check file contents in:
VTK-x.y.z/ThirdParty/PACKAGE/CMakeLists.txt
look for the number under "VERSION".
This is what VTK was designed for, but we can often push the version higher.

**NOTE: To change the version, it must either match the MAJOR version number,
  or,
  add a line to deps.set\_property(..."cmake\_config\_version\_compat", "AnyNewerVersion")
  so find_\_package() will allow a much newer version to be flagged as compatible.**

So, gather the information we need (some libraries are not so consistent):
* **VTK-PACKAGE-NAME**
 * VTK calls this package "fast_float"
* **CONAN-PACKAGE-NAME**
 * Conan calls this package "fast_float"
* **VERSION-NUMBER**
 * The VTK-desired version number if 3.9.0 (from CMakeLists.txt,
   and from the error printout from `conan create`)

* Add a line to `def _third_party(self)` in the recipe, in this format:
  "VTK-PACKAGE-NAME" : [False, "CONAN-PACKAGE-NAME/VERSION-NUMBER", "CONAN-COMPONENT-NAME"],
  In this example:
  "fast_float": [False, "fast_float/3.9.0", "fast_float::fast_float"],


# NOTES - TODO for future recipe
* Support different dependencies for different VTK versions - use conandata.yml to encode the third_party(self) data ?
* Load ALL possible options from ALL json files for ALL versions, and then del options later. Rather than requiring conan to change init()


# - Read vtk's Documentation/release/9.1.md for important notes about versions and forks
# - Also read vtk's Documentation/build.md for information about build settings and flags
# - Modify build_requirements() to match the version of CMake that VTK tested with that release.
