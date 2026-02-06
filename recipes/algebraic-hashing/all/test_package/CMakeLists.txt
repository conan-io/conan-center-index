cmake_minimum_required(VERSION 3.20)
project(test_algebraic_hashing CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(AlgebraicHashing REQUIRED)

add_executable(test_algebraic_hashing test_basic_usage.cpp)
target_link_libraries(test_algebraic_hashing AlgebraicHashing::algebraic_hashing)