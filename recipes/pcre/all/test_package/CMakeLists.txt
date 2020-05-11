cmake_minimum_required(VERSION 2.8.11)
project(test_package)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
if (PCRE_STATIC)
    target_compile_definitions(${PROJECT_NAME} PRIVATE PCRE_STATIC=1)
endif (PCRE_STATIC)
