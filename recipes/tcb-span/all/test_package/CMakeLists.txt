cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(tcb-span REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cxx)
target_link_libraries(${PROJECT_NAME} PRIVATE tcb-span::tcb-span)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
