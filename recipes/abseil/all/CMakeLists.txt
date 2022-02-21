cmake_minimum_required(VERSION 3.8)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(MSVC)
    add_definitions("-D_HAS_DEPRECATED_RESULT_OF")
endif()

if(NOT CMAKE_SYSTEM_PROCESSOR)
    set(CMAKE_SYSTEM_PROCESSOR ${CONAN_ABSEIL_SYSTEM_PROCESSOR})
endif()

add_subdirectory(source_subfolder)
