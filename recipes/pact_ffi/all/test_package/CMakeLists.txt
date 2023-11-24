cmake_minimum_required(VERSION 3.15)

project(test_package C)

find_package(pact_ffi REQUIRED CONFIG)
add_executable(${PROJECT_NAME} main.c)
target_link_libraries(${PROJECT_NAME} PRIVATE pact_ffi::pact_ffi)
