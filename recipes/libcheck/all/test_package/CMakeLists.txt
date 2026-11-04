cmake_minimum_required(VERSION 3.15)
project(test_package C)

find_package(check REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(TARGET Check::checkShared)
    target_link_libraries(${PROJECT_NAME} Check::checkShared)
else()
    target_link_libraries(${PROJECT_NAME} Check::check)
endif()
