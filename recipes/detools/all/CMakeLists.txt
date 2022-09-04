cmake_minimum_required(VERSION 3.1)
project(detools C)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

add_library(detools source_subfolder/c/detools.c)
install(TARGETS detools DESTINATION lib)
install(FILES source_subfolder/c/detools.h DESTINATION include)
