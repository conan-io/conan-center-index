cmake_minimum_required(VERSION 3.1.0)
project(test_package C)

find_package(libpciaccess REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} libpciaccess::libpciaccess)
