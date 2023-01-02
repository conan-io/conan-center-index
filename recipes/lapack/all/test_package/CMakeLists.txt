cmake_minimum_required(VERSION 3.1)
project(example C)

find_package(LAPACK)

add_executable(${PROJECT_NAME} example.c)
target_link_libraries(${PROJECT_NAME} LAPACK::LAPACKE)
set_target_properties(${PROJECT_NAME} PROPERTIES C_STANDARD 99)
