cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(maddy REQUIRED CONFIG)

add_executable(${PROJECT_NAME} example.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE maddy::maddy)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
if(maddy_VERSION VERSION_GREATER_EQUAL "1.4.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE MADDY_VERSION_1_4)
endif()
