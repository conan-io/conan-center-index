cmake_minimum_required(VERSION 2.8.11)
project(cmake_wrapper)

include("conanbuildinfo.cmake")
conan_basic_setup()

if(MSVC)
  if(MSVC_VERSION AND (MSVC_VERSION EQUAL 1910 OR MSVC_VERSION GREATER 1910))
    add_definitions(-DGTEST_LANG_CXX11=1 -DGTEST_HAS_TR1_TUPLE=0)
  endif(MSVC_VERSION AND (MSVC_VERSION EQUAL 1910 OR MSVC_VERSION GREATER 1910))
endif(MSVC)

add_subdirectory("source_subfolder")
