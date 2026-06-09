cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(LibXslt REQUIRED)
if(NOT DEFINED LIBXSLT_INCLUDE_DIR)
    message(FATAL_ERROR "LIBXSLT_INCLUDE_DIR variable not defined, expected to be set by Conan-generated CMake files")
endif()

find_package(LibXml2 REQUIRED)

add_executable(${PROJECT_NAME} libxslt_tutorial.c)
target_link_libraries(${PROJECT_NAME} PRIVATE LibXslt::LibXslt LibXml2::LibXml2)
