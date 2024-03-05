cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

add_executable(${PROJECT_NAME} test_package.cpp)

if (LLVM_SHARED)
    find_package(LLVM REQUIRED)
    target_link_libraries(${PROJECT_NAME} PRIVATE LLVM)
else()
    find_package(LLVM REQUIRED COMPONENTS LLVMSupport)
    target_link_libraries(${PROJECT_NAME} PRIVATE LLVMSupport)
endif()
