cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(zyre REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(TARGET zyre-static)
    target_link_libraries(${PROJECT_NAME} PRIVATE zyre-static)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE zyre)
endif()
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
