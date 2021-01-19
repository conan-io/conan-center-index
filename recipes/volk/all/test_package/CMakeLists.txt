cmake_minimum_required(VERSION 3.1)
project(test_package C)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

add_executable(${PROJECT_NAME}_nolibs test_package.c)
target_compile_definitions(${PROJECT_NAME}_nolibs PRIVATE VOLK_IMPLEMENTATION)
target_link_libraries(${PROJECT_NAME}_nolibs ${CONAN_SYSTEM_LIBS_VOLK})
