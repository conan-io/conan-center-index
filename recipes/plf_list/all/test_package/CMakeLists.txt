cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(plf_list REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE plf_list::plf_list)
if (plf_list_VERSION VERSION_GREATER_EQUAL 2.70)
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
endif()
