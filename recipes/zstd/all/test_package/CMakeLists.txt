cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/logo.png
     DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

find_package(zstd REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)

# Note: assuming that only one of these targets exists
target_link_libraries(${PROJECT_NAME} $<TARGET_NAME_IF_EXISTS:zstd::libzstd_shared>)
target_link_libraries(${PROJECT_NAME} $<TARGET_NAME_IF_EXISTS:zstd::libzstd_static>)
