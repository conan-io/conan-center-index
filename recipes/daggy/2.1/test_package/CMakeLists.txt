cmake_minimum_required(VERSION 3.21.0)
project(DaggyPackageTest)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(daggy REQUIRED)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_subdirectory(testcpp)
add_subdirectory(testc)
