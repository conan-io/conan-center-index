cmake_minimum_required(VERSION 3.18)
project(test_package CXX)

find_package(cpp-member-accessor CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE cpp-member-accessor::cpp-member-accessor)
