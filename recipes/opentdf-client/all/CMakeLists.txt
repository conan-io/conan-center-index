cmake_minimum_required(VERSION 2.8.12)
project(cmake_wrapper)

include("conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

# Set include paths
conan_global_flags()

add_subdirectory(source_subfolder)
