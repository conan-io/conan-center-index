cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(stringzilla REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE stringzilla::stringzilla)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
if(stringzilla_VERSION VERSION_LESS 2.0)
  target_compile_definitions(${PROJECT_NAME} PRIVATE STRINGZILLA_LESS_2_0)
endif()
