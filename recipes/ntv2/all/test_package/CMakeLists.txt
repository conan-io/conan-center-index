cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

find_package(ntv2 CONFIG REQUIRED)

add_executable(example example.cpp)
target_link_libraries(example ntv2::ntv2)

enable_testing()
add_test(NAME example
         COMMAND example)
