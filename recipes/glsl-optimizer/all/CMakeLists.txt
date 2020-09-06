cmake_minimum_required(VERSION 2.8.0)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory("source_subfolder")
# Don't build tests, 1. we don't need them, 2. tests require OpenGL on MacOS
set_target_properties(glsl_test PROPERTIES EXCLUDE_FROM_ALL TRUE)

