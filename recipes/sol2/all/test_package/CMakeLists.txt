cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(sol2 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
target_link_libraries(${PROJECT_NAME} PRIVATE sol2::sol2)

if(${sol2_CONSIDERED_VERSIONS} VERSION_GREATER_EQUAL "3.0.0")
    # include path of sol.hpp is different in v2.x.x
    target_compile_definitions(${PROJECT_NAME} PRIVATE SOL2_V3)
endif()
