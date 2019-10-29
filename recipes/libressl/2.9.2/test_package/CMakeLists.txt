cmake_minimum_required(VERSION 3.7)
project(TestPackage)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(example test.c)
target_link_libraries(example CONAN_PKG::libressl)
