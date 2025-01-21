cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(ICU REQUIRED uc)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ICU::uc)
if(ICU_VERSION VERSION_LESS "75.1")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
endif()
