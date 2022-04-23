cmake_minimum_required(VERSION 3.10.2)
project(test_package VERSION 1.0)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(ignition-cmake2 REQUIRED CONFIG)

include(IgnCMake)
ign_configure_project()
ign_configure_build()
