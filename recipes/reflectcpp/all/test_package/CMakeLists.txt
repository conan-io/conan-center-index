cmake_minimum_required(VERSION 3.30)

project(reflectcpp-test)

find_package(reflectcpp CONFIG REQUIRED)

add_executable(reflectcpp-test src/main.cpp)

target_link_libraries(
    reflectcpp-test
    reflectcpp::reflectcpp
)
