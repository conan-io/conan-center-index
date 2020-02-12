cmake_minimum_required(VERSION 2.8.12)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_MODULE_PATH ${CONAN_CMAKE_MODULE_PATH} ${CMAKE_SOURCE_DIR}/source_subfolder/build/cmake/modules ${CMAKE_MODULE_PATH})

add_subdirectory(source_subfolder)
