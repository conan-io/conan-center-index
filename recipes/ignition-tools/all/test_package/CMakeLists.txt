cmake_minimum_required(VERSION 3.8)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

set(IGN_TOOLS_MAJOR_VER "" CACHE STRING "Version of igition-tools")

if(NOT IGN_TOOLS_MAJOR_VER)
    message(FATAL_ERROR "IGN_MAJOR_MAJOR_VER not set")
endif()

find_package(ignition-tools${IGN_TOOLS_MAJOR_VER} REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ignition-tools${IGN_TOOLS_MAJOR_VER}::ignition-tools${IGN_TOOLS_MAJOR_VER})
set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS ON
)
