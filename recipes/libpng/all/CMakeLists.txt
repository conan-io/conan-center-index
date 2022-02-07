cmake_minimum_required(VERSION 3.1.2)
project(cmake_wrapper)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

if(NOT CMAKE_SYSTEM_PROCESSOR)
    set(CMAKE_SYSTEM_PROCESSOR ${CONAN_LIBPNG_SYSTEM_PROCESSOR})
endif()

add_subdirectory("source_subfolder")
