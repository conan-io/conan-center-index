cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(flann REQUIRED CONFIG)

add_executable(${CMAKE_PROJECT_NAME} test_package.c)
if(FLANN_SHARED)
  target_link_libraries(${CMAKE_PROJECT_NAME} flann::flann)
else()
  target_link_libraries(${CMAKE_PROJECT_NAME} flann::flann_s)
endif()
