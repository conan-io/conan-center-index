cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(fastdds REQUIRED CONFIG)

add_executable(${PROJECT_NAME}
    test_package.cpp
    msg/HelloWorld.cxx
    msg/HelloWorldPubSubTypes.cxx
)

set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
target_link_libraries(${PROJECT_NAME} fastrtps)
