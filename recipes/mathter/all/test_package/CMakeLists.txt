cmake_minimum_required(VERSION 3.8)
project(TestPackage CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(test_package test_package.cpp)
target_link_libraries(test_package ${CONAN_LIBS})
target_compile_features(test_package PUBLIC cxx_std_17)
