cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(SDL3_net REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)

target_link_libraries(${PROJECT_NAME} PRIVATE $<IF:$<TARGET_EXISTS:SDL3_net::SDL3_net>,SDL3_net::SDL3_net,SDL3_net::SDL3_net-static>)
