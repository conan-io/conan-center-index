cmake_minimum_required(VERSION 2.8)
project(conan_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

if (WIN32 AND BUILD_SHARED_LIBS)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif(WIN32 AND BUILD_SHARED_LIBS)

add_subdirectory(source_subfolder)
