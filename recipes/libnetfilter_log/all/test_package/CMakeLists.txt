cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(libnetfilter_log CONFIG REQUIRED)

add_executable(example example.cpp)
target_link_libraries(example libnetfilter_log::libnetfilter_log)
