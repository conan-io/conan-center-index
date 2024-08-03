cmake_minimum_required(VERSION 3.14)
project(test_package LANGUAGES C)

find_package(Fontconfig REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE Fontconfig::Fontconfig)
target_compile_features(${PROJECT_NAME} PRIVATE c_std_99)
