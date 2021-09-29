cmake_minimum_required(VERSION 3.12)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(wg21_linear_algebra REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE wg21_linear_algebra::wg21_linear_algebra)
target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_20)
