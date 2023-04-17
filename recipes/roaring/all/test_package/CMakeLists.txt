cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(roaring REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE roaring::roaring)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
if(roaring_VERSION VERSION_LESS "0.3.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE "ROARING_NO_NAMESPACE")
endif()
