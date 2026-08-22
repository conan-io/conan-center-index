cmake_minimum_required(VERSION 3.15)

project(test_package LANGUAGES CXX) # if the project uses c++

find_package(LibJuice REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)

if (BUILD_SHARED_LIBS)
    target_link_libraries(${PROJECT_NAME} PRIVATE LibJuice::LibJuice)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE LibJuice::LibJuiceStatic)
endif()
