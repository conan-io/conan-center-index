# Switching from Vendored/System requirements to Conan-sourced packages

There are plenty of modules that are NOT built by default (even if build_all_modules=True)
due to missing dependencies.  It will require additional work to make these build.

Missing dependencies are listed in "missing_from_cci" in conanfile.py

## Procedure for this list:
* for each item, check if there is a recipe in CCI (clone it for easy search)
* check VTK/ThirdParty/PACKAGE/CMakeLists.txt for minimum version
* check VTK/ThirdParty/PACKAGE/vtkPACK/README.kitware.md for any notes on special changes to the library, apart from integration with the build system.
* try adding to the "parties" list
* ensure VTK_MODULE_USE_EXTERNAL_VTK_pack is NOT set to False
* 'conan create' with the group/module enabled that requires this pack
* build with CMAKE_FIND_DEBUG_MODE=True (option below to uncomment) and carefully ensure it isn't picking up any system libs (search the output for "The item was")


## Major Versions

Note that VTK-CMake's find_package() defaults to allowing ANY newer version of a package to be used.
This is in contrast to Conan's default, which requires the major versions to match.
ie fmt 9.1.0 is the minimum, VTK will build with fmt 10.x.x
However, Conan's generated cmake files will NOT error due to compatibility.

Most of the time, Conan's default policy makes sense and is acceptable.
For those packages that we want to push further, add it to the list in the recipe:
  "allow_newer_major_versions_for_these_requirements"


## CMake file_name and target_name

Conan generates cmake files for each dependency, named the way that recipe's author decided.
These can be different to what VTK is looking for.

Add rows in the recipe to set the "cmake_file_name" and "cmake_target_name" as required.

The original CMake finder for a dependency might have also provided some non-standard variables that
the Conan recipe does not provide.  This is also the place to add them.
eg "LibPROJ_MAJOR_VERSION".

Or special include directories (eg for double-version)
