cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(cmaes CONFIG REQUIRED)

add_executable(example src/example.cpp)
target_link_libraries(example libcmaes::cmaes)
target_compile_features(example PUBLIC cxx_std_11)
