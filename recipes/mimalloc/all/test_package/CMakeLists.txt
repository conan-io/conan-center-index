cmake_minimum_required(VERSION 2.8.11)
project(PackageTest C CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(test_package test_package.c)
target_link_libraries(test_package ${CONAN_LIBS})

add_executable(test_package_cpp test_package.cpp)
target_link_libraries(test_package_cpp ${CONAN_LIBS})
