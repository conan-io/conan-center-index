cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(cpplogging CONFIG REQUIRED)

add_executable(console src/console.cpp)
target_link_libraries(console cpplogging::cpplogging)

target_compile_features(console PRIVATE cxx_std_17)
