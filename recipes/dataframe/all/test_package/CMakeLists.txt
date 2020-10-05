cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(DataFrame REQUIRED CONFIG)

if(MSVC)
  add_definitions(-DLIBRARY_EXPORTS)
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} DataFrame::DataFrame)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
