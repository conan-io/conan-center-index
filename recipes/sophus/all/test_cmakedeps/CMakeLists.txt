cmake_minimum_required(VERSION 3.15)
project(test_package)

find_package(Sophus REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} Sophus::Sophus)
