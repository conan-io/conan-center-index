cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES C)

find_package(GnuTLS REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE GnuTLS::GnuTLS)

# Test whether variables from https://cmake.org/cmake/help/latest/module/FindGnuTLS.html are properly defined
set(_custom_vars
    GNUTLS_FOUND
    GNUTLS_INCLUDE_DIR
    GNUTLS_LIBRARIES
    GNUTLS_DEFINITIONS
    GNUTLS_VERSION
)
foreach(_custom_var ${_custom_vars})
    if(DEFINED ${_custom_var})
        message(STATUS "${_custom_var}: ${${_custom_var}}")
    else()
        message(FATAL_ERROR "${_custom_var} not defined")
    endif()
endforeach()
