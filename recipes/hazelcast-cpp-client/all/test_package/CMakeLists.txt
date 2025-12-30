cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(hazelcast-cpp-client REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE hazelcast-cpp-client::hazelcast-cpp-client)
