cmake_minimum_required(VERSION 3.20)
project(test_zeroipc)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(zeroipc REQUIRED)

add_executable(test_zeroipc src/test_zeroipc.cpp)
target_link_libraries(test_zeroipc zeroipc::zeroipc)