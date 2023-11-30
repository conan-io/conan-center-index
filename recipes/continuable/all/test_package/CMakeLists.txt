cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(continuable REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD_REQUIRED ON
)
target_link_libraries(${PROJECT_NAME} PRIVATE continuable::continuable)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
