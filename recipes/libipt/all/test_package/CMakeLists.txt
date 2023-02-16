cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(libipt REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(test_package PRIVATE cxx_std_11 cxx_constexpr)
target_link_libraries(${PROJECT_NAME} libipt::libipt)
