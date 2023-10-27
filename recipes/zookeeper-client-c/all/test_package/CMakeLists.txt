cmake_minimum_required(VERSION 3.8)
project(test_package C)

find_package(zookeeper-client-c REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE zookeeper-client-c::zookeeper-client-c)
