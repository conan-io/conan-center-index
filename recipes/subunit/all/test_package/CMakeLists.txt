cmake_minimum_required(VERSION 3.15)
project(test_package C CXX)

find_package(subunit REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE subunit::subunit)
