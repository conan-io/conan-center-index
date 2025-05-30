cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(gsl-lite REQUIRED)

add_executable(${PROJECT_NAME})
if(gsl-lite_VERSION VERSION_GREATER_EQUAL "1.0.0")
    target_sources(${PROJECT_NAME} PRIVATE test_package.cpp)
    target_link_libraries(${PROJECT_NAME} PRIVATE gsl-lite::gsl-lite)
else()
    target_sources(${PROJECT_NAME} PRIVATE test_package_v0.cpp)
    target_link_libraries(${PROJECT_NAME} PRIVATE gsl::gsl-lite)
endif()

target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
