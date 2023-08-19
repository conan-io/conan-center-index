cmake_minimum_required(VERSION 3.15)

# Required because Conan does not emit `set(CMAKE_SYSTEM_NAME "GENERIC")` or
# `set(CMAKE_SYSTEM_PROCESSOR "ARM")` causing host flags to be leacked to CMake
# in the conan_toolchain.cmake
set(CMAKE_TOOLCHAIN_FILE ../toolchain.cmake)

project(test_package LANGUAGES CXX)

set(test_package_compiler_flags -mcpu=cortex-m0plus
  -mfloat-abi=soft
  --specs=nosys.specs
  --specs=nano.specs
  --specs=picolibc.specs)

add_executable(${PROJECT_NAME} main.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
target_compile_options(${PROJECT_NAME} PRIVATE ${test_package_compiler_flags})
target_link_options(${PROJECT_NAME} PRIVATE ${test_package_compiler_flags})
