cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(simple-websocket-server REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE simple-websocket-server::simple-websocket-server)
set_target_properties(
    ${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 11
    CXX_STANDARD_REQUIRED ON
)
