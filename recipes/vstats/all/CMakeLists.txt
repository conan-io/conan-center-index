cmake_minimum_required(VERSION 3.15)
project(vstat)

add_library(vstat
    src/timer.cpp
    src/loop_tracker.cpp
    src/complexity_estimator.cpp
)

target_include_directories(vstat PUBLIC include)
