cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

# Include the dlib subdirectory to skip a check
add_subdirectory(source_subfolder/dlib)
