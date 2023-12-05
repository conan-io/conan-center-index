cmake_minimum_required(VERSION 3.6)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Armadillo REQUIRED)

add_executable(example ../test_package/src/example.cpp)
target_link_libraries(example Armadillo::Armadillo)
set_property(TARGET example PROPERTY CXX_STANDARD 11)

# Test whether variables from https://cmake.org/cmake/help/latest/module/FindArmadillo.html are properly defined

set(_custom_vars
    ARMADILLO_FOUND
    ARMADILLO_INCLUDE_DIRS
    ARMADILLO_LIBRARIES
    ARMADILLO_VERSION_MAJOR
    ARMADILLO_VERSION_MINOR
    ARMADILLO_VERSION_PATCH
    ARMADILLO_VERSION_STRING
    ARMADILLO_VERSION_NAME
)
foreach(_custom_var ${_custom_vars})
    if(DEFINED ${_custom_var})
        message(STATUS "${_custom_var}: ${${_custom_var}}")
    else()
        message(FATAL_ERROR "${_custom_var} not defined")
    endif()
endforeach()
