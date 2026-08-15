cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(units REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE units::units)
if(units_VERSION VERSION_GREATER_EQUAL "3.4.0")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_23)
    target_compile_definitions(${PROJECT_NAME} PRIVATE UNITS_NEW_API)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
endif()
