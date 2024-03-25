cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

if(UNIX AND NOT APPLE)
    # use RPATH instead of RUNPATH so that
    # transitive dependencies can be located
    add_link_options("LINKER:--disable-new-dtags")
endif()

include(CTest)
enable_testing()

find_package(Boost REQUIRED)
add_executable(main_exe main.cpp)
target_link_libraries(main_exe PRIVATE Boost::predef)
add_test(NAME boost_boost COMMAND main_exe)
