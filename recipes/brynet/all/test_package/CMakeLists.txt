cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(brynet REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE brynet::brynet)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

if(brynet_VERSION VERSION_GREATER_EQUAL "1.11.2")
    target_compile_definitions(${PROJECT_NAME} PRIVATE BRYNET_EVENTLOOP_TCPSERVICE)
endif()
