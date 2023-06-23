cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(BZip2 REQUIRED)

add_executable(test_package test_package.c)
target_link_libraries(test_package PRIVATE BZip2::BZip2)

# Test whether variables from https://cmake.org/cmake/help/latest/module/FindBZip2.html are properly defined
set(_custom_vars
    BZIP2_FOUND
    BZIP2_NEED_PREFIX
    BZIP2_INCLUDE_DIRS
    BZIP2_INCLUDE_DIR
    BZIP2_LIBRARIES
    BZIP2_VERSION_STRING
)
foreach(_custom_var ${_custom_vars})
    if(DEFINED ${_custom_var})
        message(STATUS "${_custom_var}: ${${_custom_var}}")
    else()
        message(FATAL_ERROR "${_custom_var} not defined")
    endif()
endforeach()
