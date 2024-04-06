cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(imgui REQUIRED CONFIG)
find_package(imguizmo REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} imgui::imgui)
target_link_libraries(${PROJECT_NAME} imguizmo::imguizmo)
