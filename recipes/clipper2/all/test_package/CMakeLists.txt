cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(clipper2 REQUIRED CONFIG)

if(TARGET Clipper2::clipper2)
  add_executable(${PROJECT_NAME} test_package.cpp)
  target_link_libraries(${PROJECT_NAME} PRIVATE Clipper2::clipper2)
  target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
endif()

if(TARGET Clipper2::clipper2z)
  add_executable(${PROJECT_NAME}_z test_package_z.cpp)
  target_link_libraries(${PROJECT_NAME}_z PRIVATE Clipper2::clipper2z)
  target_compile_features(${PROJECT_NAME}_z PRIVATE cxx_std_17)
endif()

