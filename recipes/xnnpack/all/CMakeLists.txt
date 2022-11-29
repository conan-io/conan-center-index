cmake_minimum_required(VERSION 3.15)
project(cmake_wrapper)

if(NOT CMAKE_SYSTEM_PROCESSOR AND CONAN_XNNPACK_SYSTEM_PROCESSOR)
    set(CMAKE_SYSTEM_PROCESSOR ${CONAN_XNNPACK_SYSTEM_PROCESSOR})
endif()

find_package(cpuinfo REQUIRED CONFIG)
if(NOT TARGET cpuinfo)
    add_library(cpuinfo INTERFACE IMPORTED)
    set_property(TARGET cpuinfo PROPERTY INTERFACE_LINK_LIBRARIES cpuinfo::cpuinfo)
endif()
if(NOT TARGET clog)
    add_library(clog INTERFACE IMPORTED)
    set_property(TARGET clog PROPERTY INTERFACE_LINK_LIBRARIES cpuinfo::cpuinfo)
endif()

find_package(pthreadpool REQUIRED CONFIG)
if(NOT TARGET pthreadpool)
    add_library(pthreadpool INTERFACE IMPORTED)
    set_property(TARGET pthreadpool PROPERTY INTERFACE_LINK_LIBRARIES pthreadpool::pthreadpool)
endif()

find_package(fp16 REQUIRED CONFIG)
if(NOT TARGET fp16)
    add_library(fp16 INTERFACE IMPORTED)
    set_property(TARGET fp16 PROPERTY INTERFACE_LINK_LIBRARIES fp16::fp16)
endif()

# not a direct requirement, but we have to define this target to avoid xnnpack to download it
if(NOT TARGET fxdiv)
    add_library(fxdiv INTERFACE IMPORTED)
endif()

add_subdirectory(src)
