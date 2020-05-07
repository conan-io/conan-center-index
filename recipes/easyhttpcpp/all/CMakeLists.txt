cmake_minimum_required(VERSION 2.8.11)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(NOT CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 11)
endif()

if(WIN32 AND BUILD_SHARED_LIBS)
    add_definitions(-DEASYHTTPCPP_DLL -DEASYHTTPCPP_API_EXPORTS)
endif()

add_subdirectory("source_subfolder")

