cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(rttr REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
if(TARGET RTTR::Core)
    target_link_libraries(${PROJECT_NAME} PRIVATE RTTR::Core)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE RTTR::Core_Lib)
endif()
