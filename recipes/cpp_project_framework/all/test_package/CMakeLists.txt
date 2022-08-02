cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED True)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(test_package test_package.cpp)
target_link_libraries(test_package ${CONAN_LIBS})
