cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(chipmunk2d REQUIRED CONFIG)

add_executable(example example.c)

if(CHIPMUNK_SHARED)
  target_link_libraries(example chipmunk2d::chipmunk)
else()
  target_link_libraries(example chipmunk2d::chipmunk_static)
endif()
