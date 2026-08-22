cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX C)

find_package(libdivide REQUIRED CONFIG)

add_executable(${PROJECT_NAME}_c test_package.c)
target_link_libraries(${PROJECT_NAME}_c libdivide::libdivide)
set_target_properties(${PROJECT_NAME}_c PROPERTIES
C_STANDARD 99
LINKER_LANGUAGE C
)

add_executable(${PROJECT_NAME}_cpp test_package.cpp)
target_link_libraries(${PROJECT_NAME}_cpp libdivide::libdivide)
set_target_properties( ${PROJECT_NAME}_cpp PROPERTIES
CXX_STANDARD 11
LINKER_LANGUAGE CXX
)
