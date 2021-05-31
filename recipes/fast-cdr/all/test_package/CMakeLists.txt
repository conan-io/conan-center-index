cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(fastcdr REQUIRED)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# check if the alias target fastcdr works 
add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME}
    fastcdr
)
