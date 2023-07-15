cmake_minimum_required(VERSION 3.8)

project(test_package CXX) # if the project uses c++

find_package(vsg REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE vsg::vsg)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
