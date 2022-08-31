cmake_minimum_required(VERSION 3.12)
project(test_package LANGUAGES CXX)

find_package(boost-leaf REQUIRED CONFIG)

add_executable(${PROJECT_NAME} main.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_EXTENSIONS OFF)
target_link_libraries(${PROJECT_NAME} PRIVATE boost::leaf)
