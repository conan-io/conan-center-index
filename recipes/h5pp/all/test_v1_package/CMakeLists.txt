cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(${CMAKE_PROJECT_NAME} test_package.cpp)
target_compile_features(${CMAKE_PROJECT_NAME} PRIVATE cxx_std_17)

find_package(h5pp REQUIRED CONFIG)
target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE h5pp::h5pp)
