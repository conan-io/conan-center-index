cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(cpp-validator REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} cpp-validator::cpp-validator)
if(MSVC)
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
endif()
