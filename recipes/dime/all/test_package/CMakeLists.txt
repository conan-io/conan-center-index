cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(dime CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} dime::dime)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
