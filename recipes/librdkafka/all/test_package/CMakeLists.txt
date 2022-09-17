cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(RdKafka REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE RdKafka::rdkafka)

add_executable(${PROJECT_NAME}_cpp test_package_cpp.cpp)
target_link_libraries(${PROJECT_NAME}_cpp PRIVATE RdKafka::rdkafka++)
