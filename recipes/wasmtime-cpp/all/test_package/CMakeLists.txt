cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(wasmtime-cpp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE wasmtime-cpp::wasmtime-cpp)
target_compile_definitions(${PROJECT_NAME} PRIVATE WASMTIME_EXAMPLES_PATH="${CMAKE_CURRENT_SOURCE_DIR}")
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_EXTENSIONS OFF
)
