cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(OpenDIS REQUIRED)

add_executable(test_package_dis6 test_package.cpp)
target_link_libraries(test_package_dis6 PRIVATE OpenDIS::OpenDIS6)


add_executable(test_package_dis7 test_package.cpp)
target_compile_definitions(test_package_dis7 PRIVATE TEST_DIS7)
target_link_libraries(test_package_dis7 PRIVATE OpenDIS::OpenDIS7)
