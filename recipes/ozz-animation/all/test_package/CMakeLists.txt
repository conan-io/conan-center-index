cmake_minimum_required(VERSION 3.1)
project(test_package)

find_package(ozz-animation REQUIRED CONFIG)

add_executable(${CMAKE_PROJECT_NAME} test_package.cpp)
set_property(TARGET ${CMAKE_PROJECT_NAME} PROPERTY CXX_STANDARD 11)
set_property(TARGET ${CMAKE_PROJECT_NAME} PROPERTY CXX_STANDARD_REQUIRED ON)

target_link_libraries(${CMAKE_PROJECT_NAME}
	ozz-animation::ozz-animation
)
