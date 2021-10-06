cmake_minimum_required(VERSION 3.12)

project(test_package)
set(CMAKE_CXX_STANDARD 11)

include(${CMAKE_BINARY_DIR}/conan_paths.cmake)

find_package(SplunkOpenTelemetry REQUIRED)

add_executable(test_package test_package.cpp)

target_link_libraries(test_package ${SplunkOpenTelemetry_LIBRARIES})

target_include_directories(test_package
  PRIVATE ${SplunkOpenTelemetry_INCLUDE_DIRS}
)
