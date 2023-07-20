cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(QXmpp REQUIRED CONFIG)

set(CMAKE_CXX_STANDARD 17)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} QXmpp::QXmpp)
