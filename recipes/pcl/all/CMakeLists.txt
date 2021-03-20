cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

# PCL expects FLANN::FLANN target
find_package(flann REQUIRED CONFIG)
add_library(FLANN::FLANN INTERFACE IMPORTED)
set_property(TARGET FLANN::FLANN PROPERTY INTERFACE_LINK_LIBRARIES flann::flann)

if(WITH_QHULL)
    find_package(Qhull REQUIRED CONFIG)
    set(QHULL_INCLUDE_DIRS ${Qhull_INCLUDE_DIRS})
    set(QHULL_LIBRARIES Qhull::Qhull)
    set(HAVE_QHULL ON)
    set(HAVE_QHULL_2011 TRUE)
    set(QHULL_FOUND TRUE)
endif()

add_subdirectory(source_subfolder)
