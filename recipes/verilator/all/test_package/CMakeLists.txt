cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(verilator REQUIRED CONFIG)

add_executable(blinky
    blinky.cpp
)
verilate(blinky SOURCES blinky.v TRACE)

option(BUILD_SYSTEMC "Build SystemC example" ON)

if(BUILD_SYSTEMC)
    find_package(SystemCLanguage REQUIRED CONFIG)
    add_executable(blinky_sc
        blinky_sc.cpp
    )
    verilate(blinky_sc SOURCES blinky.v SYSTEMC)
    target_link_libraries(blinky_sc PRIVATE SystemC::systemc)
endif()
