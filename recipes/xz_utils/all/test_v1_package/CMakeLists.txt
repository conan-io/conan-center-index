cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(LibLZMA REQUIRED)

add_executable(${PROJECT_NAME} ../test_package/test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE LibLZMA::LibLZMA)

# Test whether variables from https://cmake.org/cmake/help/latest/module/FindLibLZMA.html
# are properly defined in conan generators
set(_custom_vars
    LIBLZMA_FOUND
    LibLZMA_INCLUDE_DIRS
    LIBLZMA_LIBRARIES
    LIBLZMA_VERSION_MAJOR
    LIBLZMA_VERSION_MINOR
    LIBLZMA_VERSION_PATCH
    LIBLZMA_VERSION_STRING
)
foreach(_custom_var ${_custom_vars})
    if(DEFINED _custom_var)
        message(STATUS "${_custom_var}: ${${_custom_var}}")
    else()
        message(FATAL_ERROR "${_custom_var} not defined")
    endif()
endforeach()
