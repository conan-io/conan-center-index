cmake_minimum_required(VERSION 3.10.0)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

set(IGN_UTILS_MAJOR_VER "" CACHE STRING "Version of igition-utils")

if(NOT IGN_UTILS_MAJOR_VER)
    message(FATAL_ERROR "IGN_UTILS_MAJOR_VER not set")
endif()

find_package(ignition-cmake2 REQUIRED)
find_package(ignition-utils${IGN_UTILS_MAJOR_VER} REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ignition-utils${IGN_UTILS_MAJOR_VER}::ignition-utils${IGN_UTILS_MAJOR_VER})
set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS ON
)
