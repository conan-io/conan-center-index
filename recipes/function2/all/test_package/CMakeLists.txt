cmake_minimum_required(VERSION 3.10)

project(test_package CXX)

find_package(function2 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)

target_link_libraries(${PROJECT_NAME} PRIVATE function2::function2)

target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
