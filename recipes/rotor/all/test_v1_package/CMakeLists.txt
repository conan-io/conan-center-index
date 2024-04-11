cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package("rotor" COMPONENTS asio thread REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
target_link_libraries(${PROJECT_NAME} rotor::core)
