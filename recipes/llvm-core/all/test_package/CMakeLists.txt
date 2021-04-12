cmake_minimum_required(VERSION 3.13.4)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(llvm-core)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)

if(TARGET llvm-core::interpreter)  # static libraries
    target_link_libraries(${PROJECT_NAME} PRIVATE
        llvm-core::interpreter
        llvm-core::irreader
        llvm-core::x86codegen
    )
else()  # shared library
    target_link_libraries(${PROJECT_NAME} llvm-core::llvm-core)
endif()
