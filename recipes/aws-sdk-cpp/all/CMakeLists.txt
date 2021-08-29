cmake_minimum_required(VERSION 3.5)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(cJSON REQUIRED)
find_package(tinyxml2 REQUIRED)

add_subdirectory(source_subfolder)
