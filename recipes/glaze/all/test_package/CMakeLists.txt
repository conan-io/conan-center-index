cmake_minimum_required(VERSION 3.20)
project(test_package LANGUAGES CXX)

find_package(glaze REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE glaze::glaze)
if(glaze_VERSION VERSION_GREATER_EQUAL "3.0.0")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_23)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
endif()
