cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(libuvc REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(TARGET LibUVC::UVCShared)
    target_link_libraries(${PROJECT_NAME} PRIVATE LibUVC::UVCShared)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE LibUVC::UVCStatic)
endif()
