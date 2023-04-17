cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(libcbor REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE libcbor::libcbor)

if(libcbor_VERSION VERSION_GREATER_EQUAL "0.10.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE -DLIBCBOR_DEPRECATE_CUSTOM_ALLOC)
endif()
