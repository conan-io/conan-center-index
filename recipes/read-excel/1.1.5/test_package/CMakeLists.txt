cmake_minimum_required(VERSION 3.1)

set( CMAKE_CXX_STANDARD 14 )

set( CMAKE_CXX_STANDARD_REQUIRED ON )

project(read-excel.test)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

include_directories(${CONAN_INCLUDE_DIRS_READ-EXCEL})

add_executable(${PROJECT_NAME} example.cpp)

target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
