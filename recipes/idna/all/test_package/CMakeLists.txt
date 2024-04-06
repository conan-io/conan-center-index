cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(ada-idna REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ada-idna)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
