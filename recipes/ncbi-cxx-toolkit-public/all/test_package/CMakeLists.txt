cmake_minimum_required(VERSION 3.15)
project(test_package)
set(PackageName ncbi-cxx-toolkit-public)

find_package(${PackageName} REQUIRED CONFIG)
add_executable(${PROJECT_NAME} basic_sample.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ${PackageName}::${PackageName})
