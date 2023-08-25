cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(libnfnetlink REQUIRED CONFIG)

add_executable(example example.cpp)
target_link_libraries(example libnfnetlink::libnfnetlink)
