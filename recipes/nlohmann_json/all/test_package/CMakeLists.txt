cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(nlohmann_json REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE nlohmann_json::nlohmann_json)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
