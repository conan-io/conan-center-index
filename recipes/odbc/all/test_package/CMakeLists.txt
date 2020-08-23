cmake_minimum_required(VERSION 2.8.12)
PROJECT(PackageTest CXX)

set(CMAKE_CXX_STANDARD 14)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(example example.cpp)
conan_target_link_libraries(example)
