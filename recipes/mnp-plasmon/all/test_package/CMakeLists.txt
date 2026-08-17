cmake_minimum_required(VERSION 3.15)
project(test_package C)

find_package(mnp_plasmon CONFIG REQUIRED)

add_executable(example src/example.c)
target_link_libraries(example PRIVATE mnp_plasmon::mnp_plasmon)
