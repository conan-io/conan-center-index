cmake_minimum_required(VERSION 3.15)

project(hello-conan LANGUAGES CXX)

add_library(hello-conan src/hello-conan.cpp)

target_include_directories(hello-conan PUBLIC include)
set_target_properties(hello-conan PROPERTIES PUBLIC_HEADER "include/hello-conan.h")
install(TARGETS hello-conan)
