cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(commata REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE commata::commata)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)

if (commata_VERSION VERSION_LESS "0.2.7")
    target_compile_definitions(${PROJECT_NAME} PRIVATE "COMMATA_VERSION_LESS_0_2_7")
endif()
