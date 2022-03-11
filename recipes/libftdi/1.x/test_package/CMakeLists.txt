cmake_minimum_required(VERSION 3.10)

project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(LibFTDI1 REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(test_package
    PRIVATE LibFTDI1::ftdipp)

