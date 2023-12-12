cmake_minimum_required(VERSION 3.15)
project(test_package C)

find_package(pdfium REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE pdfium::pdfium)
