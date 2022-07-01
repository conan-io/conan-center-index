cmake_minimum_required(VERSION 3.1)

project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(NO_OUTPUT_DIRS)

if(NOT CMAKE_SYSTEM_PROCESSOR)
    set(CMAKE_SYSTEM_PROCESSOR ${CONAN_LIBJPEG_SYSTEM_PROCESSOR})
endif()


add_subdirectory("source_subfolder")
