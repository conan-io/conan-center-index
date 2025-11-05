cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(avro-cpp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE 
    $<TARGET_NAME_IF_EXISTS:avro-cpp::avrocpp_s>
    $<TARGET_NAME_IF_EXISTS:avro-cpp::avrocpp>
    )
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
