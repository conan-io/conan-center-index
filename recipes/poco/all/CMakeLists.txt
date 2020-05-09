cmake_minimum_required(VERSION 2.8.12)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

# Disable automatic linking on MSVC
add_definitions(-DPOCO_NO_AUTOMATIC_LIBS)

add_subdirectory(source_subfolder)
