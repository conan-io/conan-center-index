cmake_minimum_required(VERSION 3.15)

project(test_package CXX)

find_package(pinocchio REQUIRED)

add_executable(${PROJECT_NAME} src/test_package.cpp)
target_link_libraries(${PROJECT_NAME} pinocchio::pinocchio)
