cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(libboxes CONFIG REQUIRED)



add_executable(example src/example.cpp)
target_link_libraries(example libboxes::libboxes)
target_compile_features(example PRIVATE cxx_std_20)
