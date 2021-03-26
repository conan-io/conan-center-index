cmake_minimum_required(VERSION 3.1.3)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} CONAN_PKG::cxxopts)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
