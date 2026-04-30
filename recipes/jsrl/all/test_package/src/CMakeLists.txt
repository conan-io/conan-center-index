cmake_minimum_required(VERSION 3.15)
project(JsrlTest CXX)


find_package(jsrl REQUIRED CONFIG)

add_executable(test_jsrl test_package.cpp)
target_link_libraries(test_jsrl PRIVATE jsrl::jsrl)
