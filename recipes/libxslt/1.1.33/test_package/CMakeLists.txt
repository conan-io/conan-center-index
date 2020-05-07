cmake_minimum_required(VERSION 3.0.2)
project(libxslt_tutorial)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} libxslt_tutorial.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

CHECK_LIBRARY_EXISTS(rt clock_gettime "" HAVE_CLOCK_GETTIME)

if (HAVE_CLOCK_GETTIME)
    target_link_libraries(${PROJECT_NAME} rt)
endif()
