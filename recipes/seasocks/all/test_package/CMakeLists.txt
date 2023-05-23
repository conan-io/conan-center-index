cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(Seasocks REQUIRED CONFIG)
find_package(Threads REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE Seasocks::seasocks Threads::Threads)
if(Seasocks_VERSION VERSION_LESS "1.4.5")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
endif()
