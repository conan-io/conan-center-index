cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

include(CheckCXXCompilerFlag)

find_package(xtensor REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE xtensor)

foreach(flag "-march=native" "-mtune=native")
  check_cxx_compiler_flag(${flag} COMPILER_SUPPORTS_MARCH_NATIVE)
  if(COMPILER_SUPPORTS_MARCH_NATIVE)
    target_compile_options(${PROJECT_NAME} PRIVATE ${flag})
  endif()
endforeach()

if (xtensor_VERSION VERSION_LESS "0.26.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE "XTENSOR_VERSION_LESS_0_26_0")
endif()
