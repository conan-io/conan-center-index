cmake_minimum_required(VERSION 2.8.11)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

# Include the dlib subdirectory to skip a check
add_subdirectory(source_subfolder/dlib)
