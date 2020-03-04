cmake_minimum_required(VERSION 2.8.12)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(test_package test_package.cpp)
target_link_libraries(test_package ${CONAN_LIBS})
set_target_properties(test_package PROPERTIES CXX_STANDARD 11)
target_compile_definitions(test_package PRIVATE THRUST_DEVICE_SYSTEM=THRUST_DEVICE_SYSTEM_OMP)
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU")
    set_target_properties(test_package PROPERTIES LINK_FLAGS -fopenmp COMPILE_OPTIONS -fopenmp)
endif()