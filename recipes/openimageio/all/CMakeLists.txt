cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include("${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

include_directories(
    BEFORE
    "${CMAKE_SOURCE_DIR}/source_subfolder/src/include"
    "${CMAKE_BINARY_DIR}/source_subfolder/src/include"
    "${CMAKE_BINARY_DIR}/source_subfolder/include"
)

add_subdirectory(source_subfolder)
