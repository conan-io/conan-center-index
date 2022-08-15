cmake_minimum_required(VERSION 3.0)
project(cmake_wrapper)

include(${CONAN_INSTALL_FOLDER}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

set(CMAKE_OBJC_FLAGS "${CMAKE_OBJC_FLAGS} ${CMAKE_C_FLAGS}")

add_subdirectory(source_subfolder)
