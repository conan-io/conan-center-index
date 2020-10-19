cmake_minimum_required(VERSION 3.10.2)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(ignition-cmake2 REQUIRED CONFIG)

include(IgnUtils)

ign_configure_build()
ign_add_executable(${PROJECT_NAME} test_package.cpp)
