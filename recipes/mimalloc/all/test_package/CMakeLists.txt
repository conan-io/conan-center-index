cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(mimalloc REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE $<IF:$<TARGET_EXISTS:mimalloc>,mimalloc,mimalloc-static>)
target_compile_features(${PROJECT_NAME} PRIVATE c_std_99)
