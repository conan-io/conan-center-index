cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(audiofile REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE audiofile::audiofile)

if (audiofile_VERSION VERSION_GREATER_EQUAL "1.1.1")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
endif()
