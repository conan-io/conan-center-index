cmake_minimum_required(VERSION 3.1.2)

project(cmake_wrapper)
message(WARNING "Conan Open62541 Wrapped CMake")

include(conanbuildinfo.cmake)
conan_basic_setup(NO_OUTPUT_DIRS)
add_subdirectory(source_subfolder)

