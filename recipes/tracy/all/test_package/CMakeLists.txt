cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(Tracy REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE Tracy::TracyClient)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
if(Tracy_VERSION VERSION_GREATER_EQUAL "0.9")
    target_compile_definitions(${PROJECT_NAME} PRIVATE TRACY_GE_0_9)
endif()
