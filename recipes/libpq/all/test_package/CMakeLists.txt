cmake_minimum_required(VERSION 2.8.11)
project(test_package)

find_package(PostgreSQL)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PostgreSQL::PostgreSQL)
