cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(Crc32c CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE Crc32c::crc32c)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
