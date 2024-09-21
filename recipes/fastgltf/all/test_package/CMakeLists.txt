cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(fastgltf REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE fastgltf::fastgltf)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
if(fastgltf_VERSION VERSION_GREATER_EQUAL "0.7.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE FASTGLTF_0_7_0_LATER)
elseif(fastgltf_VERSION VERSION_GREATER_EQUAL "0.5.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE FASTGLTF_0_5_0_LATER)
endif()
