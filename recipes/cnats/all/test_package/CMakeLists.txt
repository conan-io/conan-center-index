cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(cnats REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if (TARGET cnats::nats_static)
    target_link_libraries(${PROJECT_NAME} PRIVATE cnats::nats_static)
else()
    # shared
    target_link_libraries(${PROJECT_NAME} PRIVATE cnats::nats)
endif()
