cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

find_package(pole CONFIG REQUIRED)

add_executable(${PROJECT_NAME} src/test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE  pole::pole)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

