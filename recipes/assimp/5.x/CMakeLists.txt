cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

if(WIN32)
  add_definitions(-DNOMINMAX)
endif()

if (CONAN_LIBS_DRACO)
  add_definitions( -DASSIMP_ENABLE_DRACO )
endif()

add_subdirectory("source_subfolder")
