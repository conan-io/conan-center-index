cmake_minimum_required(VERSION 3.15)
project(WaveletBufferTest CXX)

find_package(wavelet_buffer CONFIG REQUIRED)

add_executable(example src/example.cpp)
target_compile_features(example PUBLIC cxx_std_20)
target_link_libraries(example wavelet_buffer::wavelet_buffer)
