cmake_minimum_required(VERSION 3.8)

project(test_package LANGUAGES CXX)

find_package(AzureSDK CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cc)
target_link_libraries(${PROJECT_NAME} PRIVATE azure-sdk-for-cpp::azure-sdk-for-cpp)
