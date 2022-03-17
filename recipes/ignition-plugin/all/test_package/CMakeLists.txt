cmake_minimum_required(VERSION 3.10.0)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(ignition-cmake2)
find_package(ignition-plugin1)
find_package(ignition-plugin1-loader)

set(IGN_PLUGIN_MAJOR_VER "" CACHE STRING "Version of igition-utils")

if(NOT IGN_PLUGIN_MAJOR_VER)
    message(FATAL_ERROR "IGN_PLUGIN_MAJOR_VER not set")
endif()

find_package(ignition-cmake2 REQUIRED)
find_package(ignition-plugin${IGN_PLUGIN_MAJOR_VER} REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} 
                    ignition-plugin${IGN_PLUGIN_MAJOR_VER}::ignition-plugin${IGN_PLUGIN_MAJOR_VER}
                    ignition-plugin${IGN_PLUGIN_MAJOR_VER}::ignition-plugin${IGN_PLUGIN_MAJOR_VER}-loader
                    #ignition-utils1::ignition-utils1
                    )
set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS ON
)
