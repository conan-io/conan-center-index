cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

find_package(rmlui REQUIRED CONFIG)

add_executable(${PROJECT_NAME} example.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
target_link_libraries(${PROJECT_NAME} PRIVATE rmlui::rmlui)
