cmake_minimum_required(VERSION 3.15)

set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR ARM)
set(CMAKE_TOOLCHAIN_FILE toolchain.cmake)

project(test_package LANGUAGES CXX)

set(test_package_compiler_flags -mcpu=cortex-m0plus
  -mfloat-abi=soft
  --specs=nosys.specs
  --specs=nano.specs)

add_executable(${PROJECT_NAME} main.cpp newlib.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
target_compile_options(${PROJECT_NAME} PRIVATE ${test_package_compiler_flags})
target_link_options(${PROJECT_NAME} PRIVATE ${test_package_compiler_flags})
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_EXTENSIONS OFF)
