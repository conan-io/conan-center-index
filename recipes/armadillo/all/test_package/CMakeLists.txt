cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(armadillo CONFIG REQUIRED)
if (LINK_HDF5)
    find_package(HDF5)
    set(HDF5_TARGETS HDF5::HDF5)
endif()

add_executable(example src/example.cpp)
target_link_libraries(example armadillo::armadillo ${HDF5_TARGETS})
set_property(TARGET example PROPERTY CXX_STANDARD 11)
