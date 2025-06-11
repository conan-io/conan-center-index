cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(incbin REQUIRED CONFIG)

file(WRITE ${CMAKE_BINARY_DIR}/hello_world.txt "Hello World!\n")

if(MSVC)
    add_custom_command(
        OUTPUT ${CMAKE_BINARY_DIR}/data.c
        COMMAND incbin_tool ARGS "${CMAKE_CURRENT_SOURCE_DIR}/test_package.c" -p g_ -Ssnakecase -o "${CMAKE_BINARY_DIR}/data.c"
        DEPENDS incbin::incbin
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        COMMENT "Generando data.c con incbin_tool..."
    )
    add_executable(${PROJECT_NAME} test_package.c ${CMAKE_BINARY_DIR}/data.c)
else()
    add_executable(${PROJECT_NAME} test_package.c)
endif()

target_link_libraries(${PROJECT_NAME} PRIVATE incbin::incbin)
target_compile_definitions(${PROJECT_NAME} PUBLIC INCBIN_FILE="${CMAKE_BINARY_DIR}/hello_world.txt")
