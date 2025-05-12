cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(iguana REQUIRED CONFIG)

if(iguana_VERSION VERSION_GREATER_EQUAL "1.0.6")
    add_executable(${PROJECT_NAME} test_package.cpp)
else()
    add_executable(${PROJECT_NAME} test_package_1_0_5.cpp)
endif()
target_link_libraries(${PROJECT_NAME} PRIVATE iguana::iguana)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
