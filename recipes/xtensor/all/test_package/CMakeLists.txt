cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

include(CheckCXXCompilerFlag)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(xtensor REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} xtensor)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)

foreach(flag "-march=native" "-mtune=native")
  check_cxx_compiler_flag(${flag} COMPILER_SUPPORTS_MARCH_NATIVE)
  if(COMPILER_SUPPORTS_MARCH_NATIVE)
    target_compile_options(${PROJECT_NAME} PRIVATE ${flag})
  endif()
endforeach()
