cmake_minimum_required(VERSION 3.1)
project(example LANGUAGES C)

find_package(libnice REQUIRED CONFIG)

add_executable(${PROJECT_NAME} src/example.c)
target_link_libraries(${PROJECT_NAME} PRIVATE libnice::libnice)
