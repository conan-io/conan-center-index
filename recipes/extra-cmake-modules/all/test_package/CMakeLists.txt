cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)


find_package(ECM REQUIRED NO_MODULE)
list(APPEND CMAKE_MODULE_PATH ${ECM_MODULE_PATH})
include(ECMGenerateHeaders)

add_library(MyLib INTERFACE)
target_include_directories(MyLib INTERFACE "${CMAKE_CURRENT_SOURCE_DIR}" "${CMAKE_CURRENT_BINARY_DIR}")
ecm_generate_headers(
    MyLib_FORWARDING_HEADERS
    HEADER_NAMES Foo
    REQUIRED_HEADERS MyLib_HEADERS
)

add_executable(example example.cpp)
target_link_libraries(example MyLib)
