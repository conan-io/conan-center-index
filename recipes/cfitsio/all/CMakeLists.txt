cmake_minimum_required(VERSION 3.1.2)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)
# we also need to inject definitions of dependencies,
# since cfitsio doesn't link to CMake imported targets
conan_global_flags()

add_subdirectory("source_subfolder")
