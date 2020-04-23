cmake_minimum_required(VERSION 3.4.3)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

unset (BUILD_SHARED_LIBS CACHE)
if (NOT CMAKE_BUILD_TYPE)
    set (CMAKE_BUILD_TYPE ${JINJA2CPP_CONAN_BUILD_TYPE})
endif ()

add_subdirectory(source_subfolder)
