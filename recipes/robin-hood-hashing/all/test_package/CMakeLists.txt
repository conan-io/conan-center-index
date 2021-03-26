cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

# Testing correct name of robin-hood target
find_package(robin_hood REQUIRED CONFIG)
if(NOT TARGET robin_hood::robin_hood)
    message(FATAL_ERROR "robin_hood::robin_hood target not found")
endif()

add_executable(${CMAKE_PROJECT_NAME} test_package.cpp)
target_link_libraries(${CMAKE_PROJECT_NAME} ${CONAN_LIBS})
set_property(TARGET ${CMAKE_PROJECT_NAME} PROPERTY CXX_STANDARD 11)

