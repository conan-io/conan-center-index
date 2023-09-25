cmake_minimum_required(VERSION 3.15)
project(PackageTest)

find_package(rocket CONFIG REQUIRED)

add_executable(example src/example.cpp)
target_link_libraries(example rocket::rocket)