cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(octomap REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(TARGET octomap-static)
  target_link_libraries(${PROJECT_NAME} PRIVATE octomap-static octomath-static)
else()
  target_link_libraries(${PROJECT_NAME} PRIVATE octomap octomath)
endif()

if(octomap_VERSION VERSION_GREATER_EQUAL "1.10.0")
  target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
endif()
