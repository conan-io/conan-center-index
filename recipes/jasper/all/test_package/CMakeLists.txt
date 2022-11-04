cmake_minimum_required(VERSION 3.1)
project(test_package C)

find_package(Jasper REQUIRED CONFIG)

set(_custom_vars
    Jasper_FOUND
    Jasper_INCLUDE_DIRS
    Jasper_LIBRARIES
    Jasper_VERSION_MAJOR
    Jasper_VERSION_MINOR
    Jasper_VERSION_PATCH
    Jasper_VERSION_STRING
)
foreach(_custom_var ${_custom_vars})
if(DEFINED _custom_var)
    message(STATUS "${_custom_var}: ${${_custom_var}}")
else()
    message(FATAL_ERROR "${_custom_var} not defined")
endif()
endforeach()

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE Jasper::Jasper)
