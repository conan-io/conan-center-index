cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(ozo REQUIRED CONFIG)

add_executable(example request.cpp)
target_compile_features(example PRIVATE cxx_std_17)
target_link_libraries(example PRIVATE yandex::ozo)
