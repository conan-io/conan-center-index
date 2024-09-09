cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(Argtable3 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(Argtable3_VERSION VERSION_GREATER_EQUAL "3.2.1")
    target_link_libraries(${PROJECT_NAME} PRIVATE argtable3::argtable3)
elseif(TARGET argtable3)
    target_link_libraries(${PROJECT_NAME} PRIVATE argtable3)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE argtable3_static)
endif()
