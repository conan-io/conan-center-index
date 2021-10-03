cmake_minimum_required(VERSION 3.1.2)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(restbed_test main.cpp)
target_link_libraries(restbed_test ${CONAN_LIBS})
set_property(TARGET restbed_test PROPERTY CXX_STANDARD 14)
