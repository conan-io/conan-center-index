cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

if(CMAKE_SYSTEM_NAME MATCHES "Linux")
    set(LINUX ON)
endif()

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_C_STANDARD 11)

add_subdirectory(source_subfolder/external)
