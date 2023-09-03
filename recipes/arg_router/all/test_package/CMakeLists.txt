cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(arg_router REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE arg_router::arg_router)

if(MSVC)
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
    target_compile_options(${PROJECT_NAME} PRIVATE /Zc:__cplusplus)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
endif()
