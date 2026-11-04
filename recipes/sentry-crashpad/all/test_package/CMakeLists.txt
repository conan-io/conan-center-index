cmake_minimum_required(VERSION 3.15)

project(test_package CXX)

find_package(crashpad REQUIRED CONFIG)

if(HAS_PROXY)
  add_compile_definitions(HAS_PROXY)
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE crashpad::client)
