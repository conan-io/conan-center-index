cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(SZ3 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE SZ3::SZ3)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
if(TARGET SZ3::hdf5sz3)
    target_link_libraries(${PROJECT_NAME} PRIVATE SZ3::hdf5sz3)
    target_compile_definitions(${PROJECT_NAME} PRIVATE SZ_WITH_HDF5)
endif()
