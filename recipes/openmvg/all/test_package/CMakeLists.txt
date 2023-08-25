cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(OpenMVG REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE
    OpenMVG::openMVG_geometry
    OpenMVG::openMVG_linearProgramming
    OpenMVG::openMVG_multiview
    OpenMVG::openMVG_numeric
)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
