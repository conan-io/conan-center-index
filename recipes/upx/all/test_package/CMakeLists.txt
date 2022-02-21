cmake_minimum_required(VERSION 3.1)
project(test_package C)

if(CMAKE_C_COMPILER_ID MATCHES "AppleClang|Clang|GNU")
    add_link_options(-static)
endif()

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(${PROJECT_NAME} test_package.c)
