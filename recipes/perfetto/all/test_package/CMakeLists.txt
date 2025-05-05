cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(perfetto REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(perfetto_VERSION VERSION_LESS "31.0")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
endif()
target_link_libraries(${PROJECT_NAME} PRIVATE perfetto::perfetto)
