cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper C)

include("conanbuildinfo.cmake")
conan_basic_setup(KEEP_RPATHS)

if(MSVC AND BUILD_SHARED_LIBS)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

add_subdirectory(source_subfolder)
