cmake_minimum_required(VERSION 3.12)
project(test_package LANGUAGES CXX)

find_package(RPP REQUIRED CONFIG)

if(RPP_VERSION VERSION_GREATER_EQUAL 2)
    add_executable(${PROJECT_NAME} test_package_v2.cpp)
else()
    add_executable(${PROJECT_NAME} test_package.cpp)
endif()
target_link_libraries(${PROJECT_NAME} PRIVATE RPP::rpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
