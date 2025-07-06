cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(magic_enum REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE magic_enum::magic_enum)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
if(magic_enum_VERSION VERSION_LESS "0.9.7")
    target_compile_definitions(${PROJECT_NAME} PRIVATE MAGIC_ENUM_TOP_LEVEL_HEADER)
endif()
