## Package Templates

A brief description about each template available:

#### Autotools package

It's listed under [autotools_package](autotools_package) folder. It fits projects which use `autotools` or `make` to be built.

#### CMake package

It's listed under [cmake_package](cmake_package) folder. It fits projects which use `CMake` to be built.

####  Header only

It's listed under [header_only](header_only) folder. It fits projects which only copy header and have the same package ID always. Please note that if the library in question does have a build system (e.g. CMake, Meson, Autotools) that contains install logic - that should be the preferred starting point for the recipe. Copying files directly into the package folder should be reserved for header only libraries where the upstream project does not provide this functionality.

#### MSBuild package

It's listed under [msbuild_package](msbuild_package) folder. It fits projects which use `msbuild` to be built.

#### Prebuilt tool package

It's listed under [prebuilt_tool_package](prebuilt_tool_package) folder. It fits projects which only copy generated binaries (executables and libraries).

#### Meson package

It's listed under [meson_package](meson_package) folder. It fits projects which use `Meson` to be built.
