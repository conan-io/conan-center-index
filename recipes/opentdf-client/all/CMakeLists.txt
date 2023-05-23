cmake_minimum_required(VERSION 3.1)
project(opentdf-client)

set(CMAKE_CXX_STANDARD 17)

include(${CMAKE_SOURCE_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory(source_subfolder)
