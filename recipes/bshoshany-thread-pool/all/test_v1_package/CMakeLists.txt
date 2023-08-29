cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(bshoshany-thread-pool REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/test_package.cpp)
target_link_libraries(${PROJECT_NAME} bshoshany-thread-pool::bshoshany-thread-pool)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
