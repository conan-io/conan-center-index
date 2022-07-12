cmake_minimum_required(VERSION 3.1)
project(test_package C)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()
if(CONAN_SETTINGS_COMPILER_RUNTIME MATCHES ".*d")
    add_compile_definitions(DISABLE_FFI_CALL)
endif()

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
