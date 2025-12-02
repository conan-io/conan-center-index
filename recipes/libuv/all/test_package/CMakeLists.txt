cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(libuv REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(TARGET libuv::uv_a)
    target_link_libraries(${PROJECT_NAME} PRIVATE libuv::uv_a)
elseif(TARGET libuv::uv)
    target_link_libraries(${PROJECT_NAME} PRIVATE libuv::uv)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE uv)
endif()
