cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C CXX)

set(CMAKE_FIND_PACKAGE_PREFER_CONFIG ON)

# Use the OpenSSL config package installed by BoringSSL
find_package(OpenSSL REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
target_link_libraries(test_package PRIVATE OpenSSL::SSL OpenSSL::Crypto)
target_compile_features(test_package PRIVATE cxx_std_17)
