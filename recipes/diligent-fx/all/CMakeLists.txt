cmake_minimum_required(VERSION 3.2)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(diligent-core)
find_package(diligent-tools)

find_package(PythonInterp 3 REQUIRED)
set(FILE2STRING_PATH "${CMAKE_CURRENT_SOURCE_DIR}/script.py" CACHE INTERNAL "File2String utility")

include(BuildUtils.cmake)
add_subdirectory(source_subfolder)
