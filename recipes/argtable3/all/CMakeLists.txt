cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(CMAKE_HOST_SYSTEM_NAME STREQUAL "Linux")
    link_libraries(m)
endif()

add_subdirectory(source_subfolder)
