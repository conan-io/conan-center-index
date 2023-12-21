cmake_minimum_required(VERSION 3.15)

project(conan_test_project
        LANGUAGES CXX)

find_package(arg_router REQUIRED)

add_executable(conan_test_project "main.cpp")
target_link_libraries(conan_test_project PUBLIC arg_router::arg_router)
