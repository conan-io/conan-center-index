cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C CXX)

find_package(czmq REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
set_target_properties(${PROJECT_NAME} PROPERTIES LINKER_LANGUAGE CXX)
if(TARGET czmq-static)
    target_link_libraries(${PROJECT_NAME} PRIVATE czmq-static)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE czmq)
endif()
