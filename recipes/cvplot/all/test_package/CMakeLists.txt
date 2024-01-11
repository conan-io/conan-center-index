cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(CvPlot CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} CvPlot::CvPlot)

target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_11)
