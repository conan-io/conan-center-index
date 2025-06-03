cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(games101-cgl REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE games101-cgl::games101-cgl)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
