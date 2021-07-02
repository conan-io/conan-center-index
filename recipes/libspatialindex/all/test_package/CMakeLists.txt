cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(libspatialindex REQUIRED)

add_executable(test_package_c test_package.c)
target_link_libraries(test_package_c libspatialindex::spatialindex_c)

add_executable(test_package_cpp test_package.cpp)
target_link_libraries(test_package_cpp libspatialindex::spatialindex)
set_property(TARGET test_package_cpp PROPERTY CXX_STANDARD 11)
