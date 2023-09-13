cmake_minimum_required(VERSION 3.15)

project(test_package CXX)

find_package(ohNet REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_definitions(${PROJECT_NAME} PUBLIC "DEFINE_LITTLE_ENDIAN")
target_link_libraries(${PROJECT_NAME} PRIVATE TestFramework ohNetCore pthread)
