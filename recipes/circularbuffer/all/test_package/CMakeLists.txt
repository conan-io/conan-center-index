cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(circularbuffer CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE circularbuffer::circularbuffer)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

if(circularbuffer_VERSION VERSION_GREATER_EQUAL "1.4.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE CIRCULARBUFFER_1_4_0_LATER)
endif()
