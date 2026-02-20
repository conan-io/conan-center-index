cmake_minimum_required(VERSION 3.15)
project(JsrlTest CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(jsrl REQUIRED CONFIG)

add_executable(test_jsrl test_package.cpp)
target_link_libraries(test_jsrl PRIVATE jsrl::jsrl)
