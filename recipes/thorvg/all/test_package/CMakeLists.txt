cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(thorvg REQUIRED CONFIG)

if(thorvg_VERSION_MAJOR LESS 1)
    add_executable(${PROJECT_NAME} test_package-v0.cpp)
else()
    add_executable(${PROJECT_NAME} test_package-v1.cpp)
endif()
target_link_libraries(${PROJECT_NAME} PRIVATE thorvg::thorvg)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
