cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

set(CMAKE_CXX_STANDARD 11)
set(THREADS_PREFER_PTHREAD_FLAG ON)

find_package(nextsilicon-cpp-subprocess REQUIRED CONFIG)
find_package(Threads REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE nextsilicon-cpp-subprocess::nextsilicon-cpp-subprocess Threads::Threads)

