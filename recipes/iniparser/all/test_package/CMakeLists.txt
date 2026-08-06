cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(iniparser REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE iniparser::iniparser)

add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy
        ${CMAKE_CURRENT_SOURCE_DIR}/test_package.ini
        $<TARGET_FILE_DIR:${PROJECT_NAME}>/test_package.ini)
