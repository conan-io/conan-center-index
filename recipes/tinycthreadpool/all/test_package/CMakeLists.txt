cmake_minimum_required(VERSION 3.15)
project(PackageTest C)

find_package(tinycthreadpool REQUIRED CONFIG)

add_executable(example example.c)
target_link_libraries(example tinycthreadpool::tinycthreadpool)
target_compile_features(example PRIVATE c_std_11)
