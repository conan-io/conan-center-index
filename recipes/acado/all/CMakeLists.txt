cmake_minimum_required(VERSION 3.10)
project(cmake_wrapper)

set(CMAKE_CXX_STANDARD 11)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/cmake")

include(conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory(source_subfolder)
