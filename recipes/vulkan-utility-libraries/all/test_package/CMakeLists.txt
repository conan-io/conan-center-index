cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(VulkanUtilityLibraries REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE Vulkan::LayerSettings)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)

if(VulkanUtilityLibraries_VERSION VERSION_LESS "1.3.268")
    target_compile_definitions(${PROJECT_NAME} PRIVATE USE_PRE_268_API)
endif()
