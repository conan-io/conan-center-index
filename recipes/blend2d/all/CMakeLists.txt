cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper LANGUAGES CXX)

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
set(CMAKE_CXX_STANDARD 11)

add_subdirectory(src)
