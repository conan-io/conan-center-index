cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(indirect_value REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE indirect_value::indirect_value)
target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_20)
