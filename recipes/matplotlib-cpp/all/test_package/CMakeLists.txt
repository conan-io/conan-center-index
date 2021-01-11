cmake_minimum_required(VERSION 3.10)
project(test_package)

set(CMAKE_CXX_STANDARD 11)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(matplotlib-cpp REQUIRED)
find_package(PythonInterp REQUIRED)
find_package(PythonLibs REQUIRED)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE matplotlib-cpp::matplotlib-cpp ${PYTHON_LIBRARIES})
target_include_directories(test_package PRIVATE ${PYTHON_INCLUDE_DIRS})
