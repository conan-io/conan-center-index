cmake_minimum_required(VERSION 3.1)
project(test_package C CXX)

# Enable strict C++11
#
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Sail REQUIRED CONFIG)

# C API
add_executable(test_package_c test_package.c)
target_link_libraries(test_package_c PRIVATE SAIL::Sail)

# C++ API
add_executable(test_package_cxx test_package.cpp)
target_link_libraries(test_package_cxx PRIVATE SAIL::SailC++)
