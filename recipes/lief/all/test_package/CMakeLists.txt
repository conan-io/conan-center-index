cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(LIEF REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE LIEF::LIEF)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

# It is required for gcc 5
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
