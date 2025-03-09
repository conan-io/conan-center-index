cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

add_executable(${PROJECT_NAME} test_package.cpp)

find_package(VulkanMemoryAllocator REQUIRED CONFIG)
if(VulkanMemoryAllocator_FOUND)
    target_link_libraries(${PROJECT_NAME} PRIVATE GPUOpen::VulkanMemoryAllocator)
else()
    find_package(vulkan-memory-allocator CONFIG)
    target_link_libraries(${PROJECT_NAME} PRIVATE vulkan-memory-allocator::vulkan-memory-allocator)
endif()
