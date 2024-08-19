cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(cairomm REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)

find_package(cairomm REQUIRED CONFIG)
target_link_libraries(${PROJECT_NAME} cairomm::cairomm)
if (cairomm_VERSION VERSION_GREATER_EQUAL 1.6)
  set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
else()
  set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
endif()
