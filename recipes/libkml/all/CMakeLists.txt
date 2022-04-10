cmake_minimum_required(VERSION 3.4.3)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS KEEP_RPATHS)

if(WIN32 AND BUILD_SHARED_LIBS)
  set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

add_subdirectory("source_subfolder")
