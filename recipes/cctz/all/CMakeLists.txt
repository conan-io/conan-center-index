cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper)


if(EXISTS "${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
  include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
else()
  include(conanbuildinfo.cmake)
endif()
conan_basic_setup()

if (WIN32 AND BUILD_SHARED_LIBS)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif(WIN32 AND BUILD_SHARED_LIBS)

add_subdirectory("source_subfolder")
