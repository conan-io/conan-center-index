cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(libigl REQUIRED CONFIG)

add_executable(example example.cpp)
target_link_libraries(example igl::core)
target_compile_features(example PUBLIC cxx_std_11)
