cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(fastdds REQUIRED)

add_executable(test_package
    test_package.cpp
    msg/HelloWorld.cxx
    msg/HelloWorldPubSubTypes.cxx
)

set_property(TARGET test_package PROPERTY CXX_STANDARD 11)

target_link_libraries(test_package
    fastrtps
)
