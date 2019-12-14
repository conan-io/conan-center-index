cmake_minimum_required(VERSION 2.8.12)
project(cmake_wrapper)

set(CONANBUILDINFO_PATH "" CACHE FILEPATH "Path to folder containing conanbuildinfo.cmake")
if(NOT CONANBUILDINFO_PATH)
    message(FATAL_ERROR "CONANBUILDIFO_PATH not set")
endif()

include("${CONANBUILDINFO_PATH}/conanbuildinfo.cmake")
conan_basic_setup()

if(MSVC)
    add_definitions("-D_NOEXCEPT=noexcept")
endif()

add_subdirectory(source_subfolder)
