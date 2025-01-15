cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(incbin CONFIG REQUIRED)

file(WRITE ${CMAKE_BINARY_DIR}/hello_world.txt "Hello World!\n")

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} incbin::incbin)
target_compile_definitions(${PROJECT_NAME} PUBLIC INCBIN_FILE="${CMAKE_BINARY_DIR}/hello_world.txt")

if(MSVC)
    add_custom_command(OUTPUT data.c
            COMMAND incbin_tool
            ARGS ${CMAKE_CURRENT_LIST_DIR}/test_package.c -p g_ -Ssnakecase -o ${CMAKE_BINARY_DIR}/data.c
            WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
            COMMENT "Generating resources with incbin_tool...")
    target_sources(${PROJECT_NAME} PRIVATE ${CMAKE_BINARY_DIR}/data.c)
endif()
