cmake_minimum_required(VERSION 3.8)
project(test_package)

find_package(Vulkan REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE Vulkan::Vulkan)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
