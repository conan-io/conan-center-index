cmake_minimum_required(VERSION 3.1)
project(test_package)

find_package(crashpad REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE crashpad::client)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
