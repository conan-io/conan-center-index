cmake_minimum_required(VERSION 3.12)
project(test_package LANGUAGES CXX)

find_package(glaze REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE glaze::glaze)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
if(glaze_VERSION VERSION_LESS "1.0.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE GLAZE_USE_EXCEPTION)
endif()
