cmake_minimum_required(VERSION 3.5)
project(test_package)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(Catch2 REQUIRED)

add_executable(test_package 000-CatchMain.cpp 100-Fix-Section.cpp)
target_link_libraries(test_package PRIVATE Catch2::Catch2)

if(WITH_MAIN)
  add_executable(standalone 200-standalone.cpp)
  target_link_libraries(standalone PRIVATE Catch2::Catch2WithMain)
endif()
