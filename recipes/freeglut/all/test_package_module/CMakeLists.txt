cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(GLUT REQUIRED MODULE)
find_package(OpenGL REQUIRED)

add_executable(${PROJECT_NAME} ../test_package/test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE GLUT::GLUT OpenGL::GL)

# Test whether variables from https://cmake.org/cmake/help/latest/module/FindGLUT.html are properly defined
set(_custom_vars
    GLUT_FOUND
    GLUT_INCLUDE_DIRS
    GLUT_LIBRARIES
)
foreach(_custom_var ${_custom_vars})
    if(DEFINED ${_custom_var})
        message(STATUS "${_custom_var}: ${${_custom_var}}")
    else()
        message(FATAL_ERROR "${_custom_var} not defined")
    endif()
endforeach()
