cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(folly REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} Folly::folly)


if (${FOLLY_VERSION} VERSION_LESS "2021.07.20.00")
    set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 14)
else()
    set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
endif()
