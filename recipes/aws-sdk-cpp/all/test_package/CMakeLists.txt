cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(AWSSDK REQUIRED CONFIG)

add_subdirectory(aws-sdk-cpp-plugin)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE aws-sdk-cpp-plugin)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

if (SDK_HAS_S3)
add_executable(${PROJECT_NAME}_s3 test_package_s3.cpp)
target_link_libraries(${PROJECT_NAME}_s3 PRIVATE aws-sdk-cpp-plugin)
target_compile_features(${PROJECT_NAME}_s3 PRIVATE cxx_std_11)
endif()
