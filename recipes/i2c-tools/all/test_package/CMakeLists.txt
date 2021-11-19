cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(i2c-tools REQUIRED CONFIG)

add_executable(example example.cpp)
target_link_libraries(example PRIVATE i2c-tools::i2c-tools)
