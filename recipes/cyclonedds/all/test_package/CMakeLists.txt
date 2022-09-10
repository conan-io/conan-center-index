cmake_minimum_required(VERSION 3.15)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

if (${MSVC})
    set(CMAKE_CXX_STANDARD 17)
else() 
    set(CMAKE_CXX_STANDARD 14)
endif()

set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(cyclone-dds REQUIRED CONFIG)

add_executable(test_package main.cpp)
target_link_libraries(test_package CycloneDDS::ddsc
)
