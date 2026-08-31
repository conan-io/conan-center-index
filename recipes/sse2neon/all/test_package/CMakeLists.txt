cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(sse2neon REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if (MSVC)
    # Consumers should define Zc:preprocessor
    target_compile_options(${PROJECT_NAME} PRIVATE "/Zc:preprocessor")
endif()
target_link_libraries(${PROJECT_NAME} PRIVATE sse2neon::sse2neon)
