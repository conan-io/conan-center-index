cmake_minimum_required(VERSION 3.20)
# CMake >= 3.20 is required. There is a proto with dots in the name 'k8s.min.proto' and CMake fails to generate project files

project(googleapis)

find_package(Protobuf REQUIRED CONFIG)

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
