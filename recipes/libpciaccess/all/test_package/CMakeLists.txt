cmake_minimum_required(VERSION 3.1.0)
project(test_package)

find_package(libpciaccess)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} libpciaccess::libpciaccess)
