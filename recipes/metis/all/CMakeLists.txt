cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper LANGUAGES C)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
set(GKLIB_PATH "${CMAKE_CURRENT_LIST_DIR}/source_subfolder/GKlib" CACHE PATH "")

add_subdirectory(source_subfolder)
