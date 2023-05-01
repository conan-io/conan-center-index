cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

find_package(CycloneDDS-CXX REQUIRED)

IDLCXX_GENERATE(TARGET MessageLib FILES Message.idl)

add_executable(test_package test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE MessageLib CycloneDDS-CXX::ddscxx CycloneDDS::ddsc)
