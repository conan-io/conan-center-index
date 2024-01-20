cmake_minimum_required(VERSION 3.15)
project(PackageTest LANGUAGES C)

find_package(libnetfilter_conntrack REQUIRED CONFIG)

add_executable(example example.c)
target_link_libraries(example libnetfilter_conntrack::libnetfilter_conntrack)
