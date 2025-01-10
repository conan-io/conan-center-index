cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C) # if the project is pure C

find_package(qoi REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
# don't link to ${CONAN_LIBS} or CONAN_PKG::package
target_link_libraries(${PROJECT_NAME} PRIVATE qoi::qoi)
