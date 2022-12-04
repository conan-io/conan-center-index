cmake_minimum_required(VERSION 3.1)
project(test_package C)

find_package(Fontconfig CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE Fontconfig::Fontconfig)
set_target_properties(${PROJECT_NAME} PROPERTIES C_STANDARD 99)
