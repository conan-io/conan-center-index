cmake_minimum_required(VERSION 3.15)
project(PackageTest LANGUAGES C)

find_package(tinyalsa CONFIG REQUIRED)

add_executable(example example.c)
target_link_libraries(example tinyalsa::tinyalsa)
