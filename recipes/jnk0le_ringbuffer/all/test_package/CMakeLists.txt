cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(jnk0le_ringbuffer CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE jnk0le_ringbuffer::jnk0le_ringbuffer)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
