cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(libsvtav1 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE libsvtav1::encoder)
if (TARGET libsvtav1::decoder)
    target_link_libraries(${PROJECT_NAME} PRIVATE libsvtav1::decoder)
    target_compile_definitions(${PROJECT_NAME} PRIVATE HAVE_DECODER)
endif()
