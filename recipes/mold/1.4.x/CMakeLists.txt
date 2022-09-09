cmake_minimum_required(VERSION 3.15)
project(mold CXX)

add_executable(mold src/mold.cpp src/main.cpp)
target_include_directories(mold PUBLIC include)

install(TARGETS mold)
