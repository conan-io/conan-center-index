cmake_minimum_required(VERSION 3.12)
project(WaveletBufferTest LANGUAGES CXX)

find_package(wavelet_buffer CONFIG REQUIRED)

add_executable(test_package test_package.cpp)
target_compile_features(test_package PRIVATE cxx_std_20)
target_link_libraries(test_package PRIVATE wavelet_buffer::wavelet_buffer)
