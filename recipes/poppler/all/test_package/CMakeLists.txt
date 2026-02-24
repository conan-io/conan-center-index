cmake_minimum_required(VERSION 3.15)
project(test_package)

find_package(poppler REQUIRED)
add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE poppler::poppler)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
