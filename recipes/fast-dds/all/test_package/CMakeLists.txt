cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(fastdds REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)

target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

message(STATUS "fastdds_VERSION: ${fastdds_VERSION}")
if(fastdds_VERSION VERSION_GREATER_EQUAL "3.0.0")
    target_link_libraries(${PROJECT_NAME} fastdds)
    add_definitions(-DFASTDDS_VERSION_3)
else()
    target_link_libraries(${PROJECT_NAME} fastrtps)
endif()
