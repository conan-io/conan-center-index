cmake_minimum_required(VERSION 3.8)
project(test_package C)

set(CMAKE_C_STANDARD 11)

find_package(libBigWig REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE libbigwig::libbigwig)
target_compile_features(${PROJECT_NAME} PRIVATE c_std_${CMAKE_C_STANDARD})
