cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

option(TEST_SHARED_LIB "Use package in a shared library")
if(TEST_AS_SHARED_LIB)
    add_library(${PROJECT_NAME}2 SHARED lib.cpp)
    target_link_libraries(${PROJECT_NAME}2 ${CONAN_LIBS})
endif()
