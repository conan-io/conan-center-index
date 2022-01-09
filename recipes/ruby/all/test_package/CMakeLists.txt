cmake_minimum_required(VERSION 3.1)
project(test_package C)

find_package(Ruby REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} Ruby::Ruby)

include(CTest)
add_test(NAME ${PROJECT_NAME} COMMAND ${PROJECT_NAME})
