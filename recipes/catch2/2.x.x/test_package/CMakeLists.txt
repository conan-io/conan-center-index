cmake_minimum_required(VERSION 3.5)
project(test_package)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(Catch2 REQUIRED)

if(NOT WITH_PREFIX)
  add_executable(test_package 000-CatchMain.cpp 100-Fix-Section.cpp)
  target_link_libraries(test_package PRIVATE Catch2::Catch2)

  if(WITH_MAIN)
    add_executable(standalone 200-standalone.cpp)
    target_link_libraries(standalone PRIVATE Catch2::Catch2WithMain)
    if(WITH_BENCHMARK)
      add_executable(benchmark 300-benchmark.cpp)
      target_link_libraries(benchmark PRIVATE Catch2::Catch2WithMain)
    endif()
  endif()
else()
  add_executable(test_package 000-CatchMain.cpp 400-with-prefix.cpp)
  target_link_libraries(test_package PRIVATE Catch2::Catch2)

  if(WITH_MAIN)
    add_executable(standalone 400-with-prefix.cpp)
    target_link_libraries(standalone PRIVATE Catch2::Catch2WithMain)
  endif()
endif()
