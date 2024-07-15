cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES C)

find_package(JPEG REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE JPEG::JPEG)
target_compile_features(${PROJECT_NAME} PRIVATE c_std_99)
if (MSVC)
    target_compile_definitions(${PROJECT_NAME} PRIVATE _CRT_SECURE_NO_WARNINGS _CRT_NONSTDC_NO_WARNINGS)
endif()

