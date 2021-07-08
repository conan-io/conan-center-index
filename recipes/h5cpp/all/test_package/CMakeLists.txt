cmake_minimum_required(VERSION 3.0)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(h5cpp REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package ${CONAN_LIBS})
