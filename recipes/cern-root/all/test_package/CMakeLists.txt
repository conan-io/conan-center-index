cmake_minimum_required(VERSION 3.13)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS NO_OUTPUT_DIRS)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY bin)

find_package(ROOT REQUIRED)

include_directories(${CMAKE_CURRENT_SOURCE_DIR})
root_generate_dictionary(G__Event Event.hpp OPTIONS -inlineInputHeader LINKDEF EventLinkDef.h )

add_library(Event SHARED Event.cpp G__Event.cxx)
target_link_libraries(Event PRIVATE ROOT::ROOT)

add_executable(testrootdictionaries testrootdictionaries.cpp)
target_link_libraries(testrootdictionaries PRIVATE Event ROOT::ROOT)
