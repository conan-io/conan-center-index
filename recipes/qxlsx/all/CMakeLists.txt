cmake_minimum_required(VERSION 3.15)
project(cmake_wrapper)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

set(QXLSX_PARENTPATH ${CMAKE_CURRENT_SOURCE_DIR})
set(QXLSX_HEADERPATH ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/header/)
set(QXLSX_SOURCEPATH ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/source/)
add_subdirectory("source_subfolder")
