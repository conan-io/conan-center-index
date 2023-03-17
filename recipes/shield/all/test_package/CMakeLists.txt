cmake_minimum_required(VERSION 3.1)
project(test_package)

find_package(shield CONFIG REQUIRED)

add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} shield::shield)
