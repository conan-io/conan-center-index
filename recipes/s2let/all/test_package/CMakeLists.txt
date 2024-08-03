cmake_minimum_required(VERSION 3.15)
project(test_package C)

find_package(s2let REQUIRED CONFIG)

add_executable(${PROJECT_NAME} example.c)
target_compile_features(${PROJECT_NAME} PUBLIC c_std_99)
target_link_libraries(${PROJECT_NAME} s2let::s2let)
