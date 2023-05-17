cmake_minimum_required(VERSION 3.15)

set(CMAKE_TOOLCHAIN_FILE ../test_package/toolchain.cmake)

project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

set(test_package_compiler_flags -mcpu=cortex-m0plus
  -mfloat-abi=soft
  --specs=nosys.specs
  --specs=nano.specs)

add_executable(${PROJECT_NAME}
  ../test_package/main.cpp
  ../test_package/newlib.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
target_compile_options(${PROJECT_NAME} PRIVATE ${test_package_compiler_flags})
target_link_options(${PROJECT_NAME} PRIVATE ${test_package_compiler_flags})
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_EXTENSIONS OFF)
