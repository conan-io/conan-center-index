cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

find_package(CycloneDDS REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE CycloneDDS::ddsc)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)

if(NOT CMAKE_CROSSCOMPILING)
  IDLC_GENERATE(TARGET test_message FILES test_message.idl)
  add_executable(test_package2 test_package2.cpp)
  target_link_libraries(test_package2 PRIVATE test_message CycloneDDS::ddsc)
endif()
