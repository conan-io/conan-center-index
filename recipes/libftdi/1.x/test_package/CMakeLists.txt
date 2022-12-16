cmake_minimum_required(VERSION 3.10)

project(test_package LANGUAGES CXX)


find_package(LibFTDI1 REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME}
    PRIVATE libftdi::ftdipp)

