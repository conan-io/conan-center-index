cmake_minimum_required(VERSION 3.5)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

# Work-around for https://github.com/wjwwood/serial/issues/135
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})

add_subdirectory(source_subfolder)
