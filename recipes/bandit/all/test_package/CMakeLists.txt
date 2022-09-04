cmake_minimum_required(VERSION 3.1)
project(test_package)

find_package(bandit REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} bandit::bandit)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
