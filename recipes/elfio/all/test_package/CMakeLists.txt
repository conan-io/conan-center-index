cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(elfio REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE elfio::elfio)
if (elfio_VERSION VERSION_LESS "3.11")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
elseif (elfio_VERSION VERSION_LESS "3.12")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
endif()
