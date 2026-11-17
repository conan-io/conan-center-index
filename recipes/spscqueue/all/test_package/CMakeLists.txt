cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(SPSCQueue REQUIRED CONFIG)
find_package(Threads REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE SPSCQueue::SPSCQueue Threads::Threads)
if(SPSCQueue_VERSION VERSION_GREATER_EQUAL "2.0.0")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
endif()
