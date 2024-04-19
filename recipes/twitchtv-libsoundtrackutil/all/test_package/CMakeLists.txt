cmake_minimum_required(VERSION 3.15)
project(PackageTest LANGUAGES CXX)

find_package(twitchtv-libsoundtrackutil REQUIRED CONFIG)

add_executable(example example.cpp)
target_link_libraries(example PRIVATE twitchtv-libsoundtrackutil::twitchtv-libsoundtrackutil)
target_compile_features(example PRIVATE cxx_std_17)
