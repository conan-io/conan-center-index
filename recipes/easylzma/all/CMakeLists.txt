cmake_minimum_required(VERSION 2.6)
project(cmake_wrapper)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(NO_OUTPUT_DIRS) #Do not call conan_output_dirs_setup(), this paths are set inside the CMakeLists.

add_subdirectory("source_subfolder")
