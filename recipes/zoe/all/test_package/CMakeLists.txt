cmake_minimum_required(VERSION 3.15)

project(test_package LANGUAGES CXX)

find_package(zoe REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE zoe::zoe)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

if(zoe_VERSION VERSION_LESS 3.2)
    target_compile_definitions(${PROJECT_NAME} PRIVATE ZOE_BEFORE_3_2)
endif()
