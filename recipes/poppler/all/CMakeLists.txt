cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

if(BUILD_SHARED_LIBS)
    if(MSVC)
        set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
    endif()
else()
    add_definitions(-DPOPPLER_STATIC)
endif()

add_subdirectory(source_subfolder)
