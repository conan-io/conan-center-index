cmake_minimum_required(VERSION 3.10.2)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(IGN_MSGS_MAJOR_VER "" CACHE STRING "Version of ignition-msgs")

if(NOT IGN_MATH_MAJOR_VER)
    message(FATAL_ERROR "IGN_MSGS_MAJOR_VER not set")
endif()

find_package(ignition-msgs${IGN_MSGS_MAJOR_VER} REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ignition-msgs${IGN_MSGS_MAJOR_VER}::ignition-msgs${IGN_MSGS_MAJOR_VER})
set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS ON
)
