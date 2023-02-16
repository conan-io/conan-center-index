cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(flann REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(TARGET flann::flann_s)
    target_link_libraries(${PROJECT_NAME} PRIVATE flann::flann_s)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE flann::flann)
endif()
