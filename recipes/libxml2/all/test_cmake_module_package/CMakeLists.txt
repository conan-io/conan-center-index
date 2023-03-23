cmake_minimum_required(VERSION 3.12)
project(test_package LANGUAGES C)

find_package(LibXml2 REQUIRED MODULE)

add_executable(${PROJECT_NAME} ../test_package/test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE LibXml2::LibXml2)

# Test whether variables from https://cmake.org/cmake/help/latest/module/FindLibXml2.html
# are properly defined in conan generators
set(_custom_vars
    LibXml2_FOUND # since CMake 3.14
    LIBXML2_FOUND # until CMake 3.14
    LIBXML2_INCLUDE_DIR
    LIBXML2_INCLUDE_DIRS
    LIBXML2_LIBRARIES
    LIBXML2_DEFINITIONS
    LIBXML2_VERSION_STRING
)
foreach(_custom_var ${_custom_vars})
    if(DEFINED ${_custom_var})
        message(STATUS "${_custom_var}: ${${_custom_var}}")
    else()
        message(FATAL_ERROR "${_custom_var} not defined")
    endif()
endforeach()
