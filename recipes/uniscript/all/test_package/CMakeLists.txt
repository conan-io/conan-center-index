cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C CXX)

find_package(uniscript REQUIRED CONFIG)

add_executable(test_package_c test_package.c)
target_link_libraries(test_package_c PRIVATE uniscript::uniscript)

add_executable(test_package_cpp test_package.cpp)
target_link_libraries(test_package_cpp PRIVATE uniscript::uniscript)
target_compile_features(test_package_cpp PRIVATE cxx_std_17)
