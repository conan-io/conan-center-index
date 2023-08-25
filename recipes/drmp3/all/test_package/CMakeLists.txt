cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES C)

find_package(drmp3 CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE drmp3::drmp3)
target_compile_features(${PROJECT_NAME} PRIVATE c_std_99)
