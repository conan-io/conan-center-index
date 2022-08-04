cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(EnTT REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE EnTT::EnTT)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
if(EnTT_VERSION VERSION_LESS "3.4.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE "ENTT_LESS_3_4_0")
endif()
