cmake_minimum_required(VERSION 3.12)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(Catch2 REQUIRED CONFIG)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(NOT WITH_PREFIX)
  add_executable(standalone 100-standalone.cpp)
  target_link_libraries(standalone PRIVATE Catch2::Catch2WithMain)
  add_executable(benchmark 200-benchmark.cpp)
  target_link_libraries(benchmark PRIVATE Catch2::Catch2WithMain)
else()
  add_executable(standalone 300-standalone-with-prefix.cpp)
  target_link_libraries(standalone PRIVATE Catch2::Catch2WithMain)
  add_executable(benchmark 400-benchmark-with-prefix.cpp)
  target_link_libraries(benchmark PRIVATE Catch2::Catch2WithMain)
endif()
