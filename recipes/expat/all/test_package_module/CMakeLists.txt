cmake_minimum_required(VERSION 3.10)
project(test_package LANGUAGES C)

find_package(EXPAT REQUIRED MODULE)

add_executable(${PROJECT_NAME} ../test_package/test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE EXPAT::EXPAT)

# Test whether variables from https://cmake.org/cmake/help/latest/module/FindEXPAT.html
# are properly defined in conan generators
set(_custom_vars
    EXPAT_INCLUDE_DIRS
    EXPAT_LIBRARIES
    EXPAT_FOUND
)
foreach(_custom_var ${_custom_vars})
    if(DEFINED ${_custom_var})
        message(STATUS "${_custom_var}: ${${_custom_var}}")
    else()
        message(FATAL_ERROR "${_custom_var} not defined")
    endif()
endforeach()
