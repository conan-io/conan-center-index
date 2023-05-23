cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

find_package(hazelcast-cpp-client REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE hazelcast-cpp-client::hazelcast-cpp-client)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
