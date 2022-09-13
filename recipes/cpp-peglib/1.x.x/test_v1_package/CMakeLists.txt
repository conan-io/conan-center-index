cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(cpp-peglib CONFIG REQUIRED)

add_executable(${PROJECT_NAME} ../test_package/test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE cpp-peglib::cpp-peglib)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
