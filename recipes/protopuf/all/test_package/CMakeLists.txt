cmake_minimum_required(VERSION 3.12)
project(test_package LANGUAGES CXX)

find_package(protopuf REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE protopuf::protopuf)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
if(protopuf_VERSION VERSION_LESS 3.0.0)
    target_compile_definitions(${PROJECT_NAME} PRIVATE PROTOPUF_V2)
endif()
