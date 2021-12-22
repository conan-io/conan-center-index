cmake_minimum_required(VERSION 3.5)
project(functions-framework-cpp-test CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(functions_framework_cpp REQUIRED CONFIG)

add_executable(test_program test_program.cc)
target_link_libraries(test_program functions-framework-cpp::framework)
