cmake_minimum_required(VERSION 3.15)
project(demo)

find_package(dfp CONFIG REQUIRED)


add_executable(demo src/demo.cpp)
target_link_libraries(demo dfp::dfp)
