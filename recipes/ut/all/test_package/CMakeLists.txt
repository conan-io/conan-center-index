cmake_minimum_required(VERSION 3.1)
project(test_package)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED yes)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(test_package test_package.cpp)
target_link_libraries(test_package ${CONAN_LIBS})
