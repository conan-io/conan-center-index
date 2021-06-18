cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_custom_command(OUTPUT gram.c gram.h
    COMMAND lemon -s "${PROJECT_SOURCE_DIR}/gram.y" -d"${PROJECT_BINARY_DIR}"
    BYPRODUCTS gram.out
)

add_executable(${PROJECT_NAME} gram.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
