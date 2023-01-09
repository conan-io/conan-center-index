cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(squirrel REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
if(TARGET squirrel::squirrel_static)
    target_link_libraries(${PROJECT_NAME} PRIVATE squirrel::squirrel_static squirrel::sqstdlib_static)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE squirrel::squirrel squirrel::sqstdlib)
endif()
