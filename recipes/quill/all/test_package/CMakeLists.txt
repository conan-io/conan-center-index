cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(quill REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)

target_link_libraries(${PROJECT_NAME} PRIVATE quill::quill)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
target_compile_definitions(${PROJECT_NAME} PRIVATE QUILL_FILE_HANDLERS_API_V3_3)

