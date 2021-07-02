cmake_minimum_required(VERSION 3.12)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(args REQUIRED CONFIG)

add_executable(example example.cpp)
# FIXME: CMake imported target shouldn't be namespaced (requires https://github.com/conan-io/conan/issues/7615)
target_link_libraries(example mbits::args)
set_target_properties(example PROPERTIES
    CXX_STANDARD 20
    CXX_STANDARD_REQUIRED OFF)
