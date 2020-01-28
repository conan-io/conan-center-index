cmake_minimum_required(VERSION 2.8)
PROJECT(test_package)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

if(WITH_CATCH)
    ADD_EXECUTABLE(test_package test_catch.cpp)
endif()
if(WITH_GTEST)
    ADD_EXECUTABLE(test_package test_gtest.cpp)
endif()
if(WITH_DOCTEST)
    ADD_EXECUTABLE(test_package test_doctest.cpp)
endif()

target_link_libraries(test_package ${CONAN_LIBS})
