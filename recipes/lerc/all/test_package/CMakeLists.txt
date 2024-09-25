cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES C CXX)

find_package(lerc REQUIRED CONFIG)

add_executable(${PROJECT_NAME}_cxx test_package.cpp)
target_link_libraries(${PROJECT_NAME}_cxx PRIVATE lerc::lerc)
target_compile_features(${PROJECT_NAME}_cxx PRIVATE cxx_std_11)

add_executable(${PROJECT_NAME}_c test_package.c)
target_link_libraries(${PROJECT_NAME}_c PRIVATE lerc::lerc)
