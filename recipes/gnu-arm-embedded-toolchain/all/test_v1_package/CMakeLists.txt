cmake_minimum_required(VERSION 3.15)

set(CMAKE_TOOLCHAIN_FILE ../toolchain.cmake)

project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(${PROJECT_NAME}
  ../test_package/main.cpp
  ../test_package/newlib.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_EXTENSIONS OFF)
