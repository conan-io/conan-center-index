cmake_minimum_required(VERSION 3.8)

project(test_package LANGUAGES CXX)

find_package(exprtk REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE exprtk::exprtk)
if (MSVC)
  target_compile_options(${PROJECT_NAME} PRIVATE "/bigobj")
endif (MSVC)

target_compile_definitions(${PROJECT_NAME} PRIVATE cxx_std_11)
