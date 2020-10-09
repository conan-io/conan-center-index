cmake_minimum_required(VERSION 3.4)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(test_package test_package.cpp)
target_link_libraries(test_package ${CONAN_LIBS})
