cmake_minimum_required(VERSION 3.21.0)
project(DaggyPackageTest)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(daggy REQUIRED)

add_subdirectory(pingpong)
add_subdirectory(testcpp)
add_subdirectory(testc)
