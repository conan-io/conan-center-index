cmake_minimum_required(VERSION 3.10)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(matplotlib-cpp REQUIRED)
find_package(PythonInterp 3 REQUIRED)
find_package(PythonLibs 3 REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE matplotlib-cpp::matplotlib-cpp ${PYTHON_LIBRARIES})
target_include_directories(test_package PRIVATE ${PYTHON_INCLUDE_DIRS})
