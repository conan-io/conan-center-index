cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(vulkan-validationlayers REQUIRED CONFIG)
#find_package(VulkanLoader REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE vulkan-validationlayers::vulkan-validationlayers) #Vulkan::Loader)
