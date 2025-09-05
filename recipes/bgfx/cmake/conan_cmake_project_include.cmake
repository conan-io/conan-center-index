cmake_minimum_required(VERSION 3.15)

find_package(miniz REQUIRED CONFIG)
find_package(tinyexr REQUIRED CONFIG)
find_package(libsquish REQUIRED CONFIG)
if(UNIX AND NOT APPLE)
    find_package(wayland REQUIRED CONFIG)
endif()
