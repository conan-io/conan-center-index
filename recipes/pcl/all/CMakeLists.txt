cmake_minimum_required(VERSION 2.8.12)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(Flann REQUIRED)
add_library(FLANN::FLANN ALIAS Flann::Flann)

find_package(Qhull REQUIRED)
set(QHULL_INCLUDE_DIRS ${Qhull_INCLUDE_DIRS})
set(QHULL_LIBRARIES ${Qhull_LIBRARIES})
set(HAVE_QHULL ON)
set(HAVE_QHULL_2011 TRUE)
set(QHULL_FOUND TRUE)

add_subdirectory(source_subfolder)
