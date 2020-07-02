cmake_minimum_required(VERSION 2.8)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
