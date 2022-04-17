cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(Eigen3 REQUIRED)
set(EIGEN_INCLUDE_DIRS ${Eigen3_INCLUDE_DIRS})
set(EIGEN_FOUND TRUE)

# PCL expects FLANN::FLANN target
find_package(flann REQUIRED CONFIG)
add_library(FLANN::FLANN INTERFACE IMPORTED)
set_property(TARGET FLANN::FLANN PROPERTY INTERFACE_LINK_LIBRARIES flann::flann)
set(FLANN_FOUND TRUE)

if(WITH_QHULL)
    find_package(Qhull REQUIRED CONFIG)
    add_library(QHULL::QHULL INTERFACE IMPORTED)
    set_property(TARGET QHULL::QHULL PROPERTY INTERFACE_LINK_LIBRARIES Qhull::Qhull)
    set(QHULL_FOUND TRUE)
    set(HAVE_QHULL TRUE)
endif()

add_subdirectory(source_subfolder)
