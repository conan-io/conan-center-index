cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(tiny-optional REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE tiny-optional::tiny-optional)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)

if(NOT ${ARCH} MATCHES "x86")
    target_compile_definitions(${PROJECT_NAME} PRIVATE TINY_OPTIONAL_USE_SEPARATE_BOOL_INSTEAD_OF_UNUSED_BITS)
endif()
