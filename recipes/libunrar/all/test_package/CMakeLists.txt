cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(Libunrar REQUIRED CONFIG)
add_executable(${PROJECT_NAME} example_basic.cpp)
target_include_directories(${PROJECT_NAME} PRIVATE
        ${Libunrar_INCLUDE_DIRS}
)
target_link_libraries(${PROJECT_NAME} PRIVATE
        ${Libunrar_LIBRARIES}
)
