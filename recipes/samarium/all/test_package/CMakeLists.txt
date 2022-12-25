cmake_minimum_required(VERSION 3.15)
project(test_package)

find_package(samarium REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} samarium::samarium)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 20)
