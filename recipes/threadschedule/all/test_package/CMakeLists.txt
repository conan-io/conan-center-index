cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(ThreadSchedule CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
if(TEST_SHARED_RUNTIME)
    target_link_libraries(${PROJECT_NAME} PRIVATE ThreadSchedule::Runtime)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE ThreadSchedule::ThreadSchedule)
endif()
