cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(samurai REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)

target_link_libraries(${PROJECT_NAME} PRIVATE samurai::samurai)

if(${samurai_VERSION} VERSION_LESS "0.3.0")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
endif()