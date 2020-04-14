cmake_minimum_required(VERSION 2.8.12)
project(test_package)

if( ${BUILD_C_TEST_PACKAGE} )
    set(CMAKE_C_STANDARD 11)
else()
    set(CMAKE_CXX_STANDARD 11)
endif()

set(CMAKE_VERBOSE_MAKEFILE TRUE)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if( ${BUILD_C_TEST_PACKAGE} )

    add_executable(${PROJECT_NAME} test_package.c)

else()
    add_executable(${PROJECT_NAME} test_package.cpp)
endif()

target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
