cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(h3 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE h3::h3)

if(h3_VERSION VERSION_GREATER_EQUAL "4.0.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE "H3_VERSION_4_LATER")
endif()
