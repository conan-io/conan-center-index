cmake_minimum_required(VERSION 3.15)

project(test_package LANGUAGES CXX)

# Conan's adds host side flags to the conan_toolchain.cmake file which
# interferes with arm-none-eabi-g++. To fix this, we set CMAKE_CXX_FLAGS
# to an empty string, then provide target specific flags to the
# executable.
set(CMAKE_CXX_FLAGS "")

set(compiler_flags
  -mcpu=cortex-m0plus
  -mfloat-abi=soft
  --specs=nosys.specs
  --specs=nano.specs)

add_executable(${PROJECT_NAME} main.cpp)
target_compile_options(${PROJECT_NAME} PRIVATE ${compiler_flags})
target_link_options(${PROJECT_NAME} PRIVATE ${compiler_flags})
