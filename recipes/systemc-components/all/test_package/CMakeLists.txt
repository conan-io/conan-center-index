cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(systemc-components REQUIRED CONFIG)
find_package(SystemCLanguage REQUIRED CONFIG)
find_package(systemc-cci REQUIRED CONFIG)
find_package(ZLIB REQUIRED CONFIG)

add_executable(${PROJECT_NAME} axi-axi-example.cpp)
target_link_libraries(${PROJECT_NAME} systemc-components::systemc-components systemc-cci::systemc-cci SystemC::systemc ZLIB::ZLIB)
