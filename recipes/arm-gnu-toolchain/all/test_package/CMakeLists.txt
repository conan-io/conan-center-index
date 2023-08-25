cmake_minimum_required(VERSION 3.15)

project(test_package LANGUAGES CXX)

set(test_package_compiler_flags -mcpu=cortex-m0plus
  -mfloat-abi=soft
  --specs=nosys.specs
  --specs=nano.specs)

add_executable(${PROJECT_NAME} main.cpp)
target_compile_options(${PROJECT_NAME} PRIVATE ${test_package_compiler_flags})
target_link_options(${PROJECT_NAME} PRIVATE ${test_package_compiler_flags})
