cmake_minimum_required(VERSION 3.1)
project(test_package C)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

add_custom_command(OUTPUT ${PROJECT_BINARY_DIR}/cylarea.c
    COMMAND "${CMAKE_COMMAND}" -E make_directory tmp
    COMMAND f2c -c -Ttmp "${PROJECT_SOURCE_DIR}/cylarea.f"
    DEPENDS "${PROJECT_SOURCE_DIR}/cylarea.f"
)

add_executable(${PROJECT_NAME} test_package.c ${PROJECT_BINARY_DIR}/cylarea.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
