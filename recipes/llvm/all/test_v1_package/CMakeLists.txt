cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(LLVM REQUIRED COMPONENTS LLVMSupport)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE LLVM::LLVMSupport)

if (llvm_build_llvm_dylib)
    add_executable(${PROJECT_NAME}-dynlib test_package.cpp)
    target_link_libraries(${PROJECT_NAME}-dynlib PRIVATE LLVM::LLVM)
endif()
