cmake_minimum_required(VERSION 2.8.12)
PROJECT(conancmakewrapper)

include(conanbuildinfo.cmake)
CONAN_BASIC_SETUP()


macro(use_cxx11)
  if(CMAKE_VERSION VERSION_LESS "3.1")
    if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
      set (CMAKE_CXX_FLAGS "--std=gnu++11 ${CMAKE_CXX_FLAGS}")
    endif()
  else()
    set(CMAKE_CXX_STANDARD 11)
  endif()
endmacro(use_cxx11)

if(CXX_14)
    MESSAGE("Activating CXX_STANDARD 14")
    set(CMAKE_CXX_STANDARD 14)
else()
    MESSAGE("Not activating CXX_STANDARD 14")
    MESSAGE("Activating CXX_STANDARD 11")
    use_cxx11()
endif()


add_subdirectory("source_subfolder")
