cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(asmjit REQUIRED CONFIG)

if(asmjit_VERSION STRGREATER_EQUAL "cci.20240531")
add_executable(${PROJECT_NAME} test_package_compiler.cpp)
else()
add_executable(${PROJECT_NAME} test_package.cpp)
endif()
target_link_libraries(${PROJECT_NAME} PRIVATE asmjit::asmjit)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
