PROJECT(test_package)
cmake_minimum_required(VERSION 2.8)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

include_directories(catch2)
ADD_EXECUTABLE(test_package test_package.cpp)
target_link_libraries(test_package ${CONAN_LIBS})
