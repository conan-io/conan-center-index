cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(fastcdr REQUIRED)
find_package(fastdds REQUIRED)

add_executable(test_generated src/test_generated.cpp testPubSubTypes.cxx
                              testTypeObjectSupport.cxx)

target_link_libraries(test_generated fastcdr fastdds)

target_include_directories(test_generated PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
