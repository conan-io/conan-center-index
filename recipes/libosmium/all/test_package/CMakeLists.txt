cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(Osmium REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_include_directories(${PROJECT_NAME} PRIVATE ${OSMIUM_INCLUDE_DIRS})
target_link_libraries(${PROJECT_NAME} PRIVATE ${OSMIUM_LIBRARIES})
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
