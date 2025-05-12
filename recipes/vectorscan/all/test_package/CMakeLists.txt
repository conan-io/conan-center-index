cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(vectorscan COMPONENTS hs REQUIRED)

add_executable(hs_example hs_example.cpp)
target_link_libraries(hs_example PRIVATE hs)
target_compile_features(hs_example PRIVATE cxx_std_11)

if(BUILD_CHIMERA)
    find_package(vectorscan COMPONENTS chimera REQUIRED)
    add_executable(ch_example ch_example.cpp)
    target_link_libraries(ch_example PRIVATE chimera)
    target_compile_features(ch_example PRIVATE cxx_std_11)
endif()
