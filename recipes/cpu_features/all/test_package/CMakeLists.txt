cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(CpuFeatures REQUIRED CONFIG)

if (ANDROID)
    find_package(CpuFeaturesNdkCompat REQUIRED CONFIG)
endif()

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE CpuFeatures::cpu_features)
