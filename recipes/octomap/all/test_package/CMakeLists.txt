cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(octomap REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(TARGET octomap-static)
  target_link_libraries(${PROJECT_NAME} PRIVATE octomap-static octomath-static)
else()
  target_link_libraries(${PROJECT_NAME} PRIVATE octomap octomath)
endif()
