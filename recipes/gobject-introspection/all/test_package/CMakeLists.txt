cmake_minimum_required(VERSION 3.15)
project(test_package C)

find_package(gobject-introspection REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE gobject-introspection::gobject-introspection)
