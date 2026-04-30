cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(libuv REQUIRED CONFIG)

if ("${libuv_VERSION}" VERSION_LESS "1.45.0")
    set(LIBUV_TARGET $<IF:$<TARGET_EXISTS:uv_a>,uv_a,uv>)
else()
    set(LIBUV_TARGET $<IF:$<TARGET_EXISTS:libuv::uv_a>,libuv::uv_a,libuv::uv>)
endif()

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE ${LIBUV_TARGET})
