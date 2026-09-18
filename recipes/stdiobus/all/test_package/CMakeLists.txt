cmake_minimum_required(VERSION 3.14)
project(test_stdiobus LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(stdiobus CONFIG REQUIRED)

add_executable(test_stdiobus src/example.cpp)
target_link_libraries(test_stdiobus PRIVATE stdiobus::stdiobus)
