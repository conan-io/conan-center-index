cmake_minimum_required(VERSION 3.5)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE CONAN_PKG::mp-units)
target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_20)
