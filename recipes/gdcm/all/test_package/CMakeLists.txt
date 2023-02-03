cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

find_package(GDCM REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
include(${GDCM_USE_FILE})
target_link_libraries(${PROJECT_NAME} PRIVATE gdcmMSFF)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
