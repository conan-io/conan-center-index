cmake_minimum_required(VERSION 3.1)
project(test_package)

find_package(cqrlib REQUIRED CONFIG)

add_executable(${PROJECT_NAME}_c test_package.c)
target_link_libraries(${PROJECT_NAME}_c PRIVATE cqrlib::cqrlib)

add_executable(${PROJECT_NAME}_cpp test_package.cpp)
target_link_libraries(${PROJECT_NAME}_cpp PRIVATE cqrlib::cqrlib)
