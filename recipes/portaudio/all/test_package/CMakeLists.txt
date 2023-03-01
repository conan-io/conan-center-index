cmake_minimum_required(VERSION 3.1.0)
project(PackageTest)

find_package(portaudio CONFIG REQUIRED)

add_executable(example test_package.c)
target_link_libraries(example portaudio::portaudio)
