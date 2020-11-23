cmake_minimum_required(VERSION 2.8.11)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(NO_OUTPUT_DIRS)

include(GNUInstallDirs)

add_subdirectory("source_subfolder")
