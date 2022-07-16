cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/cmake/modules")
add_subdirectory("source_subfolder/cmake")
