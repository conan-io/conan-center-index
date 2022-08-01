cmake_minimum_required(VERSION 3.10)
project(test_package CXX)

if (${HAZELCAST_CPP_CLIENT_VERSION} VERSION_LESS_EQUAL "4.0.0")
    find_package(hazelcastcxx REQUIRED CONFIG)
else()
    find_package(hazelcast-cpp-client REQUIRED CONFIG)
endif()

add_executable(test_package test_package.cpp)
if (${HAZELCAST_CPP_CLIENT_VERSION} VERSION_LESS_EQUAL "4.0.0")
    target_link_libraries(test_package PUBLIC hazelcastcxx::hazelcastcxx)
else()
    target_link_libraries(test_package PUBLIC hazelcast-cpp-client::hazelcast-cpp-client)
endif()

set_property(TARGET test_package PROPERTY CXX_STANDARD 11)
