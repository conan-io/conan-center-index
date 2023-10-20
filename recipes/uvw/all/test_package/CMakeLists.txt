cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(uvw REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE uvw::uvw)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
if(uvw_VERSION VERSION_GREATER_EQUAL "3.0.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE UVW_API_3_0)
endif()
