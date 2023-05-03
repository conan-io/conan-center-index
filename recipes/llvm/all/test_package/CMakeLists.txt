cmake_minimum_required(VERSION 3.1)
project(test_package)

set(CMAKE_CXX_STANDARD 14)

find_package(LLVM REQUIRED COMPONENTS LLVMSupport)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} LLVMSupport)
