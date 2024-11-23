cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(reflectcpp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} reflectcpp::reflectcpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)

SET(CMAKE_EXE_LINKER_FLAGS  "${CMAKE_EXE_LINKER_FLAGS} -Wl,--copy-dt-needed-entries")
