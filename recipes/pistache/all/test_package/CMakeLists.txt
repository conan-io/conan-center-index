cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(Pistache REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE Pistache::Pistache)
if(Pistache_VERSION EQUAL "cci.20201127")
  target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
else()
  target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
endif()
