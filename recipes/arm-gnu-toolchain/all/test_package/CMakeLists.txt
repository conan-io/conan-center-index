cmake_minimum_required(VERSION 3.15)

# This is a workaround for Conan 1.x
set(CMAKE_TOOLCHAIN_FILE toolchain.cmake)

project(test_package LANGUAGES CXX)

set(test_package_compiler_flags -mcpu=cortex-m0plus
  -mfloat-abi=soft
  --specs=nosys.specs
  --specs=nano.specs)

set(CMAKE_CXX_FLAGS "")
message(AUTHOR_WARNING "CMAKE_CXX_FLAGS = ${CMAKE_CXX_FLAGS}")

add_executable(${PROJECT_NAME} main.cpp)
target_compile_options(${PROJECT_NAME} PRIVATE ${test_package_compiler_flags})
target_link_options(${PROJECT_NAME} PRIVATE ${test_package_compiler_flags})
