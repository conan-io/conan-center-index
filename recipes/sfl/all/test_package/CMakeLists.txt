cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(sfl REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE sfl::sfl)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
if(sfl_VERSION VERSION_GREATER_EQUAL 2.0.0)
    target_compile_definitions(${PROJECT_NAME} PRIVATE SFL_VERSION=2)
else()
    target_compile_definitions(${PROJECT_NAME} PRIVATE SFL_VERSION=1)
endif()
