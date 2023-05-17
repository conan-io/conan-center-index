cmake_minimum_required(VERSION 3.8)

project(test_package CXX)

find_package(nmos-cpp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE nmos-cpp::compile-settings nmos-cpp::nmos-cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
