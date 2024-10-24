cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(thorvg REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE thorvg::thorvg)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
if (THORVG_VERSION_LESS_1)
    target_compile_definitions(${PROJECT_NAME} PRIVATE THORVG_VERSION_LESS_1)
endif()
