cmake_minimum_required(VERSION 3.8)
project(test_package C)

find_package(BigWig REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE BigWig::BigWig)
target_compile_features(${PROJECT_NAME} PRIVATE c_std_11)
