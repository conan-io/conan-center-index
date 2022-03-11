cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(gemmlowp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} gemmlowp::eight_bit_int_gemm)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
