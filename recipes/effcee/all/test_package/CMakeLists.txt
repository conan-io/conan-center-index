cmake_minimum_required(VERSION 3.1)
project(test_package)

if(NOT CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 11)
endif()

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(effcee REQUIRED)

add_executable(effcee-example main.cc)

target_link_libraries(effcee-example effcee::effcee)
