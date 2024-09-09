cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(cgltf REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE cgltf::cgltf)
if(MSVC)
  target_compile_definitions(${PROJECT_NAME} PRIVATE _CRT_SECURE_NO_WARNINGS)
endif()
