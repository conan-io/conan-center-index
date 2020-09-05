cmake_minimum_required(VERSION 3.5)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if (BUILD_SHARED_LIBS AND MSVC)
  # Building a dll
  add_definitions(-DWEBP_DLL)
endif()

add_subdirectory("source_subfolder")
