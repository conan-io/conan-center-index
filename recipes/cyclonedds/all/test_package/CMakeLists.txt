cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

find_package(CycloneDDS REQUIRED CONFIG)

IDLC_GENERATE(TARGET MessageLib FILES Message.idl)

add_executable(test_package test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE MessageLib CycloneDDS::ddsc)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
