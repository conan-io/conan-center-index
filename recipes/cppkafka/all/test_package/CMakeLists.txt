cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGET)

find_package(cppkafka CONFIG REQUIRED)


add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} cppkafka::cppkafka)

set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 11)
