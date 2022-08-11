cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)


if(WIN32)
    set(CMAKE_REQUIRED_LIBRARIES ws2_32)
endif()

add_subdirectory(src)
