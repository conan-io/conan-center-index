cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

# include(CMakePackageConfigHelpers)

find_package(g1fitting CONFIG REQUIRED)

add_executable(test_g1fitting main.cpp)
target_link_libraries(test_g1fitting g1fitting::g1fitting)
