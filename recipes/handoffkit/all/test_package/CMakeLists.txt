cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(handoffkit REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(TARGET handoffkit::core)
  target_link_libraries(${PROJECT_NAME} PRIVATE handoffkit::core)
else()
  target_link_libraries(${PROJECT_NAME} PRIVATE handoffkit::handoffkit)
endif()
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
