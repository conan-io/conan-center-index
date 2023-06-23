cmake_minimum_required(VERSION 3.12)
project(test_package LANGUAGES CXX)

find_package(Platform.Interfaces REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE Platform.Interfaces::Platform.Interfaces)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)

if(Platform.Interfaces_VERSION VERSION_GREATER_EQUAL "0.2.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE -DPLATFORM_INTERFACES_0_2_0_LATER)
endif()
