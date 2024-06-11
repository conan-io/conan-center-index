cmake_minimum_required(VERSION 3.12)
project(test_package LANGUAGES CXX)

find_package(libhal REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_EXTENSIONS OFF)
target_link_libraries(${PROJECT_NAME} PRIVATE libhal::libhal)
if(libhal_VERSION VERSION_LESS "2.0.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE LIBHAL_LESS_2)
endif()
