cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(stduuid REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE stduuid::stduuid)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
if(stduuid_VERSION VERSION_LESS "1.1")
    target_compile_definitions(${PROJECT_NAME} PRIVATE STDUUID_LT_1_1)
endif()
