cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper)

find_package(fxdiv REQUIRED CONFIG)
if(NOT TARGET fxdiv)
    add_library(fxdiv INTERFACE IMPORTED)
    set_property(TARGET fxdiv PROPERTY INTERFACE_LINK_LIBRARIES fxdiv::fxdiv)
endif()

add_subdirectory(src)
