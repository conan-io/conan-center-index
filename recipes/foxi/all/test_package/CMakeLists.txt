cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(foxi REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_compile_definitions(${PROJECT_NAME} PRIVATE ONNXIFI_PATH="${ONNXIFI_PATH}")
target_link_libraries(${PROJECT_NAME} PRIVATE foxi_loader)
