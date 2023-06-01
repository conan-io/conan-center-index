cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(chaiscript REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)

target_link_libraries(${PROJECT_NAME} PRIVATE chaiscript::chaiscript)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
if (WIN32)
    target_compile_options(${PROJECT_NAME} PRIVATE /bigobj)
endif()
