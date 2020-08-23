cmake_minimum_required(VERSION 3.0)
project(conanzyre)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(NOT BUILD_SHARED_LIBS)
    add_definitions(-DZYRE_STATIC)
endif()

add_subdirectory(source_subfolder)
