cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)
include(conanbuildinfo.cmake)

list(APPEND CONAN_BASIC_SETUP_ARGS TARGETS NO_OUTPUT_DIRS)

if(APPLE)
  list(APPEND CONAN_BASIC_SETUP_ARGS KEEP_RPATHS)
endif()

conan_basic_setup(${CONAN_BASIC_SETUP_ARGS})
add_subdirectory("source_subfolder")
