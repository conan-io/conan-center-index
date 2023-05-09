cmake_minimum_required(VERSION 3.1)
project(test_package)

find_package(LLVM REQUIRED COMPONENTS LLVMSupport)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} LLVMSupport)

if (llvm_build_llvm_dylib)
    find_package(LLVM REQUIRED COMPONENTS LLVM)
    add_executable(${PROJECT_NAME}-dynlib test_package.cpp)
    target_link_libraries(${PROJECT_NAME} LLVM)
endif()
