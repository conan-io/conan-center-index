cmake_minimum_required(VERSION 3.15)

project(test_package CXX)

find_package(libp2p REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE p2p::p2p_multiaddress)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
