cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(nuraft CONFIG REQUIRED)

add_executable(${PROJECT_NAME})
target_sources(${PROJECT_NAME} PRIVATE test_package.cpp)
target_link_libraries(${PROJECT_NAME} nuraft::nuraft)
target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_11)
