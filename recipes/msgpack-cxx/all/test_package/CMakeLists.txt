cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(msgpack REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(msgpack_VERSION VERSION_GREATER_EQUAL "6.0.0")
    target_link_libraries(${PROJECT_NAME} msgpack-cxx)
else()
    target_link_libraries(${PROJECT_NAME} msgpackc-cxx)
endif()
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
