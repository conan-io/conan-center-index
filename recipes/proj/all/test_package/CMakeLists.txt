cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(test_package test_package.c)
if(PROJ_VERSION_GE_7)
  find_package(proj REQUIRED)
  target_link_libraries(test_package PROJ::proj)
else()
  find_package(proj4 REQUIRED)
  target_link_libraries(test_package PROJ4::proj)
endif()
