cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(OpenJPEG REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE openjp2)

# Test whether variables from https://github.com/uclouvain/openjpeg/blob/master/cmake/OpenJPEGConfig.cmake.in are properly defined
set(_custom_vars
    OPENJPEG_FOUND
    OPENJPEG_INCLUDE_DIRS
    OPENJPEG_LIBRARIES
    OPENJPEG_MAJOR_VERSION
    OPENJPEG_MINOR_VERSION
    OPENJPEG_BUILD_VERSION
    OPENJPEG_BUILD_SHARED_LIBS
)
foreach(_custom_var ${_custom_vars})
    if(DEFINED ${_custom_var})
        message(STATUS "${_custom_var}: ${${_custom_var}}")
    else()
        message(FATAL_ERROR "${_custom_var} not defined")
    endif()
endforeach()
