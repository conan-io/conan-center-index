cmake_minimum_required(VERSION 3.12)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(${PROJECT_NAME} example.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE CONAN_PKG::confu_json)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
