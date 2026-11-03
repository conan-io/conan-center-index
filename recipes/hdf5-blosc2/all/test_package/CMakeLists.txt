cmake_minimum_required(VERSION 3.15)

project(test_package LANGUAGES C)

find_package(hdf5-blosc2 REQUIRED CONFIG)
find_package(HDF5 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE hdf5-blosc2::hdf5-blosc2 HDF5::HDF5)
