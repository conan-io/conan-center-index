cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(p7 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)

if(P7_SHARED)
  target_link_libraries(${PROJECT_NAME} p7::p7-shared)
else()
  target_link_libraries(${PROJECT_NAME} p7::p7)
endif()
