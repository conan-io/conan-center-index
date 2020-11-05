cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(sigc++-2 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} sigc++-2::sigc++-2) # TODO: Disable namespace
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
