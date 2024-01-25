cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(gfx-timsort REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE gfx::timsort)

if(gfx-timsort_VERSION VERSION_LESS "2.0.0")
  target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_98)
elseif(gfx-timsort_VERSION VERSION_LESS "3.0.0")
  target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
else()
  target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
endif()
