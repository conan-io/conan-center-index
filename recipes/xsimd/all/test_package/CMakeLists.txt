cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(CheckCXXCompilerFlag)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(xsimd REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} xsimd::xsimd)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 14)

if (CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
  foreach(flag "/arch:AVX")
    CHECK_CXX_COMPILER_FLAG(${flag} COMPILER_SUPPORTS_MARCH_NATIVE)
    if(COMPILER_SUPPORTS_MARCH_NATIVE)
      target_compile_options(${PROJECT_NAME} PRIVATE ${flag})
    endif()
  endforeach()
elseif ((CMAKE_CXX_COMPILER_ID STREQUAL "GNU") OR (CMAKE_CXX_COMPILER_ID STREQUAL "Clang")  OR (CMAKE_CXX_COMPILER_ID STREQUAL "AppleClang"))
  foreach(flag "-march=native" "-mtune=native")
    CHECK_CXX_COMPILER_FLAG(${flag} COMPILER_SUPPORTS_MARCH_NATIVE)
    if(COMPILER_SUPPORTS_MARCH_NATIVE)
      target_compile_options(${PROJECT_NAME} PRIVATE ${flag})
    endif()
  endforeach()
endif()
