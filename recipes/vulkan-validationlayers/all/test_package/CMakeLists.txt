cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(vulkan-validationlayers REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE vulkan-validationlayers::vulkan-validationlayers)
if(vulkan-validationlayers_VERSION VERSION_GREATER_EQUAL "1.3.235")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
endif()
