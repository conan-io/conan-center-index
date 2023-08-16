cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(hyperscan COMPONENTS hs REQUIRED)

add_executable(hs_example hs_example.cpp)
target_link_libraries(hs_example PRIVATE hyperscan::hs)
target_compile_features(hs_example PRIVATE cxx_std_11)

if(BUILD_CHIMERA)
    find_package(hyperscan COMPONENTS chimera REQUIRED)
    add_executable(ch_example ch_example.cpp)
    target_link_libraries(ch_example PRIVATE hyperscan::chimera)
    target_compile_features(ch_example PRIVATE cxx_std_11)
endif()
