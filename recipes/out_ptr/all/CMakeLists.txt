cmake_minimum_required(VERSION 3.15)
project(out_ptr CXX)

add_library(out_ptr src/out_ptr.cpp)
target_include_directories(out_ptr PUBLIC include)

set_target_properties(out_ptr PROPERTIES PUBLIC_HEADER "include/out_ptr.h")
install(TARGETS out_ptr)
