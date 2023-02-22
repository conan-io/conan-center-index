cmake_minimum_required(VERSION 3.1)
project(test_package)

find_package(doctest REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
target_link_libraries(${PROJECT_NAME} doctest::doctest)

enable_testing()

add_test(NAME ${PROJECT_NAME} COMMAND ${PROJECT_NAME})
