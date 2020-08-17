cmake_minimum_required(VERSION 3.12)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} si_package_test.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
