cmake_minimum_required(VERSION 3.1)
project(test_package)

list(APPEND CMAKE_PREFIX_PATH ${CMAKE_BINARY_DIR})
find_package(aws-cdi-sdk REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} aws-cdi-sdk::aws-cdi-sdk)
