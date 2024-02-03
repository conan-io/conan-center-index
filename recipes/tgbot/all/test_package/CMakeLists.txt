cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(tgbot REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
target_link_libraries(${PROJECT_NAME} tgbot::tgbot)
