cmake_minimum_required(VERSION 2.8.12)
project(PackageTest CXX)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

find_package(verilator REQUIRED)

add_executable(blinky
    blinky.cpp
)
verilate(blinky SOURCES blinky.v TRACE)

add_executable(blinky_sc
    blinky_sc.cpp
)
verilate(blinky_sc SOURCES blinky.v SYSTEMC)
target_link_libraries(blinky_sc PRIVATE CONAN_PKG::systemc)
