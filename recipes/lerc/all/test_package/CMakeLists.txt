cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(lerc REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE lerc::lerc)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

if(lerc_VERSION VERSION_GREATER_EQUAL "3.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE -DLERC_VER3_LATER)
endif()
