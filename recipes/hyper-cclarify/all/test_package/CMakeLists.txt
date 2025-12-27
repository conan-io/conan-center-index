cmake_minimum_required(VERSION 3.15)
project(cclarify_test C)

find_package(hyper-cclarify CONFIG REQUIRED)

set(CMAKE_C_FLAGS "-O0 -g")
set(CMAKE_CXX_FLAGS "-O0 -g")

add_executable(cclarify-tests
    ${CMAKE_CURRENT_SOURCE_DIR}/../dist/munit/munit.c
    ${PROJECT_SOURCE_DIR}/src/tests.c)
target_include_directories(cclarify-tests PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/../dist/munit)
target_link_libraries(cclarify-tests hyper-cclarify::hyper-cclarify)
