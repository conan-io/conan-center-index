cmake_minimum_required(VERSION 2.8.12)

project(cmake_wrapper)
message(WARNING "Conan libMySQLclient Wrapped CMake")

include(../conanbuildinfo.cmake)
conan_basic_setup(NO_OUTPUT_DIRS)
include("CMakeListsOriginal.txt")
