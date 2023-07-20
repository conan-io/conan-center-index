cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(xege REQUIRED CONFIG)

add_executable(example example.cpp)
target_link_libraries(example PRIVATE xege::xege)

if(MSYS OR MINGW)
    target_link_libraries(example -static-libgcc -static-libstdc++)
endif()
