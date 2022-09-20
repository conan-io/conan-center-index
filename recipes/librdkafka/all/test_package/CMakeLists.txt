cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C CXX)

find_package(RdKafka REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE RdKafka::rdkafka)

add_executable(${PROJECT_NAME}_cpp test_package.cpp)
target_link_libraries(${PROJECT_NAME}_cpp PRIVATE RdKafka::rdkafka++)
