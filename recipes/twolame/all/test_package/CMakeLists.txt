cmake_minimum_required(VERSION 3.15)
project(test_twolame C)

find_package(twolame REQUIRED CONFIG)

add_executable(test_twolame test_twolame.c)
target_link_libraries(test_twolame PRIVATE twolame::twolame)
