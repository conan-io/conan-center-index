cmake_minimum_required(VERSION 3.15)
project(PackageTest NONE)

find_package(SWIG REQUIRED CONFIG)

# Checks on what the conan-swig-variables.cmake build module should provide
if(NOT SWIG_EXECUTABLE OR NOT EXISTS "${SWIG_EXECUTABLE}")
    message(FATAL_ERROR "SWIG_EXECUTABLE not set or missing: '${SWIG_EXECUTABLE}'")
endif()
if(NOT EXISTS "${SWIG_DIR}/swig.swg")
    message(FATAL_ERROR "SWIG_DIR does not point at swiglib: '${SWIG_DIR}'")
endif()
if(NOT TARGET SWIG::SWIG)
    message(FATAL_ERROR "SWIG::SWIG target missing")
endif()
