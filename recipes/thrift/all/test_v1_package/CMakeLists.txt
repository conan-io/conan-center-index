cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Thrift CONFIG REQUIRED)

add_executable(${PROJECT_NAME}
    ../test_package/calculator_constants.cpp
    ../test_package/calculator_types.cpp
    ../test_package/Calculator.cpp
    ../test_package/test_package.cpp
)
target_link_libraries(${PROJECT_NAME} PRIVATE thrift::thrift)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
