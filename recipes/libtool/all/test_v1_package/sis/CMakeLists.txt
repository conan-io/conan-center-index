cmake_minimum_required(VERSION 3.1)
project(static_dependency C)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)
add_library(static_lib STATIC
    static_lib.c
)
install(TARGETS static_lib
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
)
