cmake_minimum_required(VERSION 3.15)
project(cpp-bencoding CXX)




add_library(cpp-bencoding src/cpp-bencoding.cpp)
target_include_directories(cpp-bencoding PUBLIC include)



set_target_properties(cpp-bencoding PROPERTIES PUBLIC_HEADER "include/cpp-bencoding.h")
install(TARGETS cpp-bencoding)
