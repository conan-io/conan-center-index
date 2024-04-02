cmake_minimum_required(VERSION 3.15)
project(test_package C)

find_package(libslz REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} libslz::libslz)
set_target_properties(${PROJECT_NAME} PROPERTIES
    C_STANDARD 11
    C_EXTENSIONS ON
)
