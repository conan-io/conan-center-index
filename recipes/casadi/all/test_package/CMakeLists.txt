cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(casadi REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE casadi::casadi)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
if(CASADI_STATIC_PLUGINS)
  target_compile_definitions(${PROJECT_NAME} PRIVATE CASADI_STATIC_PLUGINS)
endif()
