cmake_minimum_required(VERSION 3.1 FATAL_ERROR)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(example example.cpp UrlTest.cpp)
target_link_libraries(example CONAN_PKG::oatpp)
set_property(TARGET example PROPERTY CXX_STANDARD 11)
set_property(TARGET example PROPERTY CMAKE_VERBOSE_MAKEFILE TRUE)
