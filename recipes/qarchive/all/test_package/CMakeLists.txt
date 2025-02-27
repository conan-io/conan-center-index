cmake_minimum_required(VERSION 3.16)
project(test_package CXX)

find_package(QArchive REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)

target_link_libraries(${PROJECT_NAME} PRIVATE QArchive)
