cmake_minimum_required(VERSION 2.8.11)
project(cmake_wrapper)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

if(CMAKE_SYSTEM_NAME MATCHES "Linux")
    set(LINUX ON)
endif()

add_subdirectory(source_subfolder/external)
