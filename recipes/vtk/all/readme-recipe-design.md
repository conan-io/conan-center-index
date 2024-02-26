# Recipe Design

## VTK Modules - modules.json --> self.options

VTK has a LOT of internal modules, with lots of dependencies and lots of external requirements,
all depending on which modules are enabled.

VTK already has a sophisticated CMake-based module-enabling and dependency system.

VTK builds generate a "modules.json" file that details all this, but only for the modules that were built.
This recipe has a script that parses the source and generates a full modules-x.y.z.json file
that is included in the recipe and used to automatically populate the options and requirements
for whichever version is chosen to build.

Our generated modules-x.y.z.json file is made with the same format as VTK's,
and when the package is built, we deploy VTK's generated modules.json file and use that
in the "package_info()" method.

In theory, we can use our pre-made full modules.json file, but I thought it better to use
the VTK-generated file.  There might be some inconsistencies that cause conan-build errors,
however this is a good thing - we should eliminate any inconsistencies.


## External Requirements - prefer CCI packages over vendored and system versions

Additional work is in the recipe to translate VTK's external requirements to existing Conan packages.

Normally, VTK builds with a lot of internally vendored libraries.  Many of these libraries do not have
any special patches or changes - they did in the past, but it appears those changes have been upstreamed.

Vendored libraries can be swapped out for whatever available in the Conan world.

By default:
* Vendored libraries are only built IF we have not specified to use a Conan package.
* Any system libraries are NOT used where possible.

This recipe-author's goal is for consumers of this recipe to work on any missing dependencies
to build modules that they are interested in building.

There are notes on how to make this happen in readme-support-dependency.md


## AUTOINIT

VTK uses a Factory pattern in some places, which requires the implementations of interfaces
to be initialized at some point.

VTK has a sophisticated autoinit system that is automatically generated for VTK-cmake-consumers,
which we cannot provide to our recipe consumers.

Instead, the autoinit mechanism is replicated by this recipe, and the appropriate header files
are generated for recipe consumers.
Note that these header implementations are different to VTK's official headers (due to being generated
by different code), but the resulting files should be the same.

There are additional notes in the recipe: look for "VTK AUTOINIT".

