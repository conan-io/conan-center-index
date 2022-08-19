cmake_minimum_required(VERSION 3.1...3.21)

set(CMAKE_C_COMPILER "gcc-11")
set(CMAKE_CXX_COMPILER "g++-11")

project(test_package VERSION 0.0.1 LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conan_paths.cmake)

find_package(libhal REQUIRED)

add_executable(${PROJECT_NAME} main.cpp)

target_include_directories(${PROJECT_NAME} PUBLIC .)
target_compile_options(${PROJECT_NAME} PRIVATE
  -Werror -Wall -Wextra -Wno-psabi -Wno-unused-function -Wconversion)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_VISIBILITY_PRESET hidden)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_EXTENSIONS OFF)
target_link_libraries(${PROJECT_NAME} PRIVATE libhal::libhal)
