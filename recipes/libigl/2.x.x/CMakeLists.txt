cmake_minimum_required(VERSION 2.8)
project(conanlibigl)

include(conanbuildinfo.cmake)
conan_basic_setup()

find_package(Eigen3 REQUIRED)

add_subdirectory(source_subfolder)
