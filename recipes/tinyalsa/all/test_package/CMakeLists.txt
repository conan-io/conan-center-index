cmake_minimum_required(VERSION 3.1)
project(PackageTest LANGUAGES C)

find_package(tinyalsa CONFIG REQUIRED)

add_executable(example example.c)
target_link_libraries(example tinyalsa::tinyalsa)
