cmake_minimum_required(VERSION 3.1.2)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(srt REQUIRED)

add_executable(${CMAKE_PROJECT_NAME} test_package.cpp)
target_link_libraries(${CMAKE_PROJECT_NAME} srt::srt)
