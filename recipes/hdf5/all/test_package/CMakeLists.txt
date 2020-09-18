cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

option(HDF5_SHARED "HDF5 is built as shared library")

find_package(hdf5 REQUIRED)

add_executable(${CMAKE_PROJECT_NAME} test_package.cpp)
if(HDF5_SHARED)
    target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE hdf5::hdf5_cpp-shared)
else()
    target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE hdf5::hdf5_cpp-static)
endif()
