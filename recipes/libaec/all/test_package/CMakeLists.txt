cmake_minimum_required(VERSION 3.1.3)
project(test_package C)

find_package(libaec CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} libaec::libaec)
