cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

enable_testing()

find_package(dylib REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE dylib::dylib)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

add_test(NAME ${PROJECT_NAME} COMMAND ${PROJECT_NAME})
