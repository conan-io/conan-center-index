cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(platform_folders REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE sago::platform_folders)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
