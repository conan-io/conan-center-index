cmake_minimum_required(VERSION 3.1)
project(PackageTest LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(stx REQUIRED)

add_executable(example_basic example.cpp)
target_link_libraries(example_basic PRIVATE CONAN_PKG::stx)
target_compile_options(example_basic PRIVATE $<$<CXX_COMPILER_ID:MSVC>:/permissive->)

add_executable(example_find_package example.cpp)
target_link_libraries(example_find_package PRIVATE stx::stx)
target_compile_options(example_find_package PRIVATE $<$<CXX_COMPILER_ID:MSVC>:/permissive->)
