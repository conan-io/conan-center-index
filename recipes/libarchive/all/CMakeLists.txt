cmake_minimum_required(VERSION 2.8.12)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(CMAKE_CROSSCOMPILING)
    if(WIN32 AND NOT CYGWIN)
        set(ZLIB_WINAPI_EXITCODE "0")
        set(ZLIB_WINAPI_EXITCODE__TRYRUN_OUTPUT "")
    endif()
endif()

add_subdirectory("source_subfolder")
