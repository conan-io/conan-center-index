cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(CLUEstering REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE CLUEstering::CLUEstering)
target_compile_definitions(${PROJECT_NAME} PRIVATE ALPAKA_ACC_CPU_B_SEQ_T_SEQ_ENABLED)
