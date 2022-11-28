cmake_minimum_required(VERSION 3.8)

project(test_package C)

find_package(szip REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(TARGET szip-shared)
    target_link_libraries(${PROJECT_NAME} szip-shared)
else ()
    target_link_libraries(${PROJECT_NAME} szip-static)
endif ()
