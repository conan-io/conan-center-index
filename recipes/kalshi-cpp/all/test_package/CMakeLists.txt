cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(kalshi REQUIRED CONFIG)
find_package(OpenSSL REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE kalshi::kalshi OpenSSL::Crypto)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_23)
