cmake_minimum_required(VERSION 3.0)
project(cmake_wrapper)

include(${CONAN_INSTALL_FOLDER}/conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

if(UNIX AND NOT APPLE)
  if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
    if(CMAKE_CXX_COMPILER_VERSION VERSION_LESS 5.0)
      add_definitions("-DGBM_BO_USE_CURSOR=2")
    endif()
  endif()
endif()

add_subdirectory(source_subfolder)
