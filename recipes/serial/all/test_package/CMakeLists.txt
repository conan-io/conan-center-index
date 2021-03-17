cmake_minimum_required(VERSION 3.1.0)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

# Test components
find_package(serial REQUIRED)
add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} serial::serial)
