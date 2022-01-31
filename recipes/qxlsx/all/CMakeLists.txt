cmake_minimum_required(VERSION 3.15.6)
project(cmake_wrapper)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

set(QXLSX_PARENTPATH ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/QXlsx)
set(QXLSX_HEADERPATH ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/QXlsx/header/)
set(QXLSX_SOURCEPATH ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/QXlsx/source/)
add_subdirectory("source_subfolder/QXlsx")
