cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(Jasper REQUIRED)

set(_custom_vars
    JASPER_FOUND
    JASPER_INCLUDE_DIR
    JASPER_LIBRARIES
    JASPER_VERSION_STRING
)
foreach(_custom_var ${_custom_vars})
if(DEFINED ${_custom_var})
    message(STATUS "${_custom_var}: ${${_custom_var}}")
else()
    message(FATAL_ERROR "${_custom_var} not defined")
endif()
endforeach()

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE Jasper::Jasper)
