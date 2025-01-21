cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(aws-lambda-runtime REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE AWS::aws-lambda-runtime)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

if(NOT COMMAND aws_lambda_package_target)
    message(FATAL_ERROR "aws_lambda_package_target should have been defined as part of find_package(aws-lambda-runtime)")
endif()
