cmake_minimum_required(VERSION 3.8)

project(test_package LANGUAGES CXX)

find_package(bgfx REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
target_link_libraries(${PROJECT_NAME} bgfx::bgfx)
