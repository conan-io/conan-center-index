project(test_package CXX)
cmake_minimum_required(VERSION 2.8.12)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${CMAKE_PROJECT_NAME} test_package.cpp)
target_link_libraries(${CMAKE_PROJECT_NAME} ${CONAN_LIBS})
target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE ${CONAN_INCLUDE_DIRS})
set_property(TARGET ${CMAKE_PROJECT_NAME} PROPERTY CXX_STANDARD 11)

option(TEST_SHARED_LIB "Use package in a shared library")
if(TEST_AS_SHARED_LIB)
    add_library(${CMAKE_PROJECT_NAME}2 SHARED lib.cpp)
    target_link_libraries(${CMAKE_PROJECT_NAME}2 ${CONAN_LIBS})
    target_include_directories(${CMAKE_PROJECT_NAME}2 PRIVATE ${CONAN_INCLUDE_DIRS})
    set_property(TARGET ${CMAKE_PROJECT_NAME}2 PROPERTY CXX_STANDARD 11)
endif()
