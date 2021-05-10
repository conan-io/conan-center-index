cmake_minimum_required(VERSION 3.1)

set( CMAKE_CXX_STANDARD 14 )

set( CMAKE_CXX_STANDARD_REQUIRED ON )

project(args-parser.test)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

include_directories(${CONAN_INCLUDE_DIRS_ARGS-PARSER})

add_executable(${PROJECT_NAME} example.cpp)

target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
