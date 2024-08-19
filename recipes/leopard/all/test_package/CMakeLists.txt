cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(ThreadPool REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ThreadPool::ThreadPool)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)

if(ThreadPool_VERSION VERSION_LESS 2.1.0)
    target_compile_definitions(${PROJECT_NAME} PRIVATE "THREADPOOL_LESS_2_1_0")
endif()
