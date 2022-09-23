cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(Thrift CONFIG REQUIRED)

add_executable(${PROJECT_NAME}
    calculator_constants.cpp
    calculator_types.cpp
    Calculator.cpp
    test_package.cpp
)
target_link_libraries(${PROJECT_NAME} PRIVATE thrift::thrift)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
