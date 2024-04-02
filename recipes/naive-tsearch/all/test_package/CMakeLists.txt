cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(naive-tsearch REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(TARGET naive-tsearch::naive-tsearch-hdronly)
    target_link_libraries(${PROJECT_NAME} PRIVATE naive-tsearch::naive-tsearch-hdronly)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE naive-tsearch::naive-tsearch)
endif()
