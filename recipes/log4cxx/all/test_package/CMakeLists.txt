cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

find_package(log4cxx REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_17)
target_include_directories(${PROJECT_NAME} PRIVATE ${log4cxx_INCLUDE_DIR})
target_link_libraries(${PROJECT_NAME} PRIVATE log4cxx::log4cxx)
