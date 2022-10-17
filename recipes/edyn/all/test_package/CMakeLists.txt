cmake_minimum_required(VERSION 3.1)

project(test_package CXX)

find_package(Edyn REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 17 CXX_STANDARD_REQUIRED ON)
target_link_libraries(${PROJECT_NAME} Edyn::Edyn)
