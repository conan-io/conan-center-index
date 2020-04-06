cmake_minimum_required(VERSION 2.8.12)
project(TestPackage CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(basic basic.cpp)
target_link_libraries(basic ${CONAN_LIBS})
set_property(TARGET basic PROPERTY CXX_STANDARD 17)
