cmake_minimum_required(VERSION 3.24)

project(test_package LANGUAGES CXX)

find_package(unicode_ranges REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_23)
target_link_libraries(${PROJECT_NAME} PRIVATE unicode_ranges::unicode_ranges)

if(MSVC)
    target_compile_options(${PROJECT_NAME} PRIVATE /utf-8 /bigobj)
endif()
