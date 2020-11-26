cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

option(TEST_LIBRARY "Build test library")
if(TEST_LIBRARY)
    # Test building a shared library.
    # a static libx265.a on Linux requires linker flags to avoid PIC related relocation errors.
    add_library(test_library SHARED test_library.c)
    target_link_libraries(test_library ${CONAN_LIBS})

    target_compile_definitions(${PROJECT_NAME} PRIVATE WITH_LIB)
    target_link_libraries(${PROJECT_NAME} test_library)
endif()
