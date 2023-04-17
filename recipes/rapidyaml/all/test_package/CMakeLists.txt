cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(ryml REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ryml::ryml)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
if(ryml_VERSION VERSION_GREATER_EQUAL "0.4.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE RYML_USE_PARSE_IN_ARENA)
endif()
