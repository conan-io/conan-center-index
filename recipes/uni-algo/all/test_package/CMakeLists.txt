cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(uni-algo REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE uni-algo::uni-algo)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)

if(uni-algo_VERSION VERSION_LESS "0.7.0")
  target_compile_definitions(${PROJECT_NAME} PRIVATE -DUNI_ALGO_NAMESPACE_UNI)
endif()
