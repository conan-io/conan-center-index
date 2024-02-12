cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(lua REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} lua::lua)
if(COMPILE_AS_CPP)
  target_compile_definitions(${PROJECT_NAME} PRIVATE COMPILE_AS_CPP)
endif()
