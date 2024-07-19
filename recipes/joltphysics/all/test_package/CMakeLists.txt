cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

add_definitions(-DJPH_PROFILE_ENABLED=0 -DJPH_DEBUG_RENDERER=0)

find_package(joltphysics REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE joltphysics::joltphysics)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
