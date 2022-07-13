cmake_minimum_required(VERSION 3.15)
project(gdal_cmake_wrapper)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

set(CMAKE_MODULE_PATH "${CMAKE_BINARY_DIR}")

file(GLOB CONAN_GENERATED_CMAKE_FILES "${CMAKE_BINARY_DIR}/Find*.cmake")
foreach(CMAKE_FILE ${CONAN_GENERATED_CMAKE_FILES})
    include(${CMAKE_FILE})
endforeach()

add_subdirectory("source_subfolder")
