cmake_minimum_required(VERSION 3.8)

project(test_package CXX) # if the project uses c++

find_package(vsg REQUIRED CONFIG)
find_package(vsgXchange REQUIRED CONFIG)
find_package(Vulkan REQUIRED CONFIG)
find_package(Curl REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE vsgXchange::vsgXchange)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
