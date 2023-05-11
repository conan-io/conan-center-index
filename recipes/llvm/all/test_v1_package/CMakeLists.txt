cmake_minimum_required(VERSION 3.1)
project(test_package)


include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} LLVMSupport)

if (llvm_build_llvm_dylib)
    add_executable(${PROJECT_NAME}-dynlib test_package.cpp)
    target_link_libraries(${PROJECT_NAME}-dynlib LLVM)
endif()
