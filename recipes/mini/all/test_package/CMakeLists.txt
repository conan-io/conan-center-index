cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(mini REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE mini::mini)
#   mini now requires at least C++17 since 0.9.17
if(mini_VERSION VERSION_GREATER "0.9.16")
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
else()
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
endif()
