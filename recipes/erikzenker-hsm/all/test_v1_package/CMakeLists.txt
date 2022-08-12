cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(hsm REQUIRED CONFIG)

add_executable(${PROJET_NAME} ../test_package/test_package.cpp)
target_link_libraries(${PROJET_NAME} PRIVATE hsm::hsm)
target_compile_features(${PROJET_NAME} PRIVATE cxx_std_17)
