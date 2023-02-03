cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

if(NOT CMAKE_SYSTEM_PROCESSOR)
    set(CMAKE_SYSTEM_PROCESSOR ${CONAN_LIBJPEG_TURBO_SYSTEM_PROCESSOR})
endif()

add_subdirectory("src")
