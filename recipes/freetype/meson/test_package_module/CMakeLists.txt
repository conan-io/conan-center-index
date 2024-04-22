cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(Freetype REQUIRED MODULE)

# Test whether variables from https://cmake.org/cmake/help/latest/module/FindFreetype.html
# are properly defined in conan generators
set(_custom_vars
    FREETYPE_FOUND
    FREETYPE_INCLUDE_DIRS
    FREETYPE_LIBRARIES
    FREETYPE_VERSION_STRING
)
foreach(_custom_var ${_custom_vars})
    if(DEFINED ${_custom_var})
        message(STATUS "${_custom_var}: ${${_custom_var}}")
    else()
        message(FATAL_ERROR "${_custom_var} not defined")
    endif()
endforeach()

add_executable(${PROJECT_NAME} ../test_package/test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE Freetype::Freetype)
