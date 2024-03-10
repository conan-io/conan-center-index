cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(cnats REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
if (TARGET cnats::nats)
    target_link_libraries(${PROJECT_NAME} PRIVATE cnats::nats)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE cnats::nats_static)
endif()
