cmake_minimum_required(VERSION 3.1)

project(test_package LANGUAGES C CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${CMAKE_PROJECT_NAME} test_package.c)
if (HDF5_CXX)
    target_compile_definitions(${CMAKE_PROJECT_NAME} PRIVATE CONAN_HDF5_CXX)
    target_sources(${CMAKE_PROJECT_NAME} PRIVATE test_package.cpp)
endif()
if (HDF5_PARALLEL)
    target_compile_definitions(${CMAKE_PROJECT_NAME} PRIVATE CONAN_HDF5_PARALLEL)
    target_sources(${CMAKE_PROJECT_NAME} PRIVATE test_parallel.c)
endif()
target_link_libraries(${CMAKE_PROJECT_NAME} ${CONAN_LIBS})
