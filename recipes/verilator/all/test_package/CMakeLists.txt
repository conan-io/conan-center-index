cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

find_package(verilator REQUIRED)

add_executable(blinky
    blinky.cpp
)
verilate(blinky SOURCES blinky.v TRACE)

option(BUILD_SYSTEMC "Build SystemC example" ON)

if(BUILD_SYSTEMC)
    add_executable(blinky_sc
        blinky_sc.cpp
    )
    verilate(blinky_sc SOURCES blinky.v SYSTEMC)
    target_link_libraries(blinky_sc PRIVATE CONAN_PKG::systemc)
endif()
