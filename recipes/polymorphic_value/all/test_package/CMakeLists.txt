cmake_minimum_required(VERSION 3.12)
project(test_package CXX)

find_package(polymorphic_value REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE polymorphic_value::polymorphic_value)
target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_20)
