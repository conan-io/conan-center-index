cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(modern-cpp-kafka REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE modern-cpp-kafka::modern-cpp-kafka)
target_compile_features(${PROJECT_NAME}  PRIVATE cxx_std_17)
