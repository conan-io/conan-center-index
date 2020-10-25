cmake_minimum_required(VERSION 3.10.2)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(SDFORMAT_VER "" CACHE STRING "Version of sdformat")

if(NOT SDFORMAT_VER)
    message(FATAL_ERROR "SDFORMAT_VER not set")
endif()

find_package(sdformat${SDFORMAT_VER} REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} sdformat${SDFORMAT_VER}::sdformat${SDFORMAT_VER})
set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS ON
)
