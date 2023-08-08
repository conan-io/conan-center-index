cmake_minimum_required(VERSION 3.15)
project(test_package C)

find_package(mdns REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE mdns::mdns)
set_target_properties(${PROJECT_NAME} PROPERTIES C_STANDARD 99)
