cmake_minimum_required(VERSION 3.1.3)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
add_subdirectory(pcl-pcl-${CONAN_PCL_VERSION})
