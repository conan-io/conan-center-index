cmake_minimum_required(VERSION 3.1)
project(test_package C)

find_package(readline CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} readline::readline)
