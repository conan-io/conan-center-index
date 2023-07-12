cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(wasm-micro-runtime REQUIRED CONFIG)

if(WAMR_NO_INTERP)
add_executable(${PROJECT_NAME} test_package_no_interp.cpp)
else()
add_executable(${PROJECT_NAME} test_package.cpp)
endif()

target_link_libraries(${PROJECT_NAME} PRIVATE wasm-micro-runtime::wasm-micro-runtime)
