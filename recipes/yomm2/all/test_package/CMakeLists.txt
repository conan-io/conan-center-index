cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(YOMM2 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE YOMM2::yomm2 ${CMAKE_THREAD_LIBS_INIT})
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
