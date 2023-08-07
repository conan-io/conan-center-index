cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(OpenAL REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE OpenAL::OpenAL)

# Test whether variables from https://cmake.org/cmake/help/latest/module/FindOpenAL.html are properly defined
set(_custom_vars
    OPENAL_FOUND
    OPENAL_INCLUDE_DIR
    OPENAL_LIBRARY
    OPENAL_VERSION_STRING
)
foreach(_custom_var ${_custom_vars})
    if(DEFINED ${_custom_var})
        message(STATUS "${_custom_var}: ${${_custom_var}}")
    else()
        message(FATAL_ERROR "${_custom_var} not defined")
    endif()
endforeach()
