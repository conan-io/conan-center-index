cmake_minimum_required(VERSION 3.6)
project(test_package)

find_package(libsigcpp REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} libsigcpp::libsigcpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
