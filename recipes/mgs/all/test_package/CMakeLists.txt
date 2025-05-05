cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(mgs REQUIRED base64 CONFIG)
add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE mgs::base64)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
