cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(libdeflate REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(TARGET libdeflate::libdeflate_static)
    target_link_libraries(${PROJECT_NAME} PRIVATE libdeflate::libdeflate_static)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE libdeflate::libdeflate)
endif()
