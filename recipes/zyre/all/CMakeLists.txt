cmake_minimum_required(VERSION 3.0)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

if(NOT BUILD_SHARED_LIBS)
    add_definitions(-DZYRE_STATIC)
endif()

add_subdirectory(source_subfolder)
