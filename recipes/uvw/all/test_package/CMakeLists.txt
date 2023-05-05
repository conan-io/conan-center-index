cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(uvw REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE uvw::uvw)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)

if(uvw_VERSION VERSION_LESS "3.0.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE UVW_VERSION_LESS_3_0_0)
endif()
