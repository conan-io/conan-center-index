cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper)

include("conanbuildinfo.cmake")
conan_basic_setup()
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

set(SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/cmp.c")
set(HEADERS "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/cmp.h")

add_library(cmp ${SOURCES} ${HEADERS})

set_target_properties(cmp PROPERTIES PUBLIC_HEADER ${HEADERS})

install(TARGETS cmp)
