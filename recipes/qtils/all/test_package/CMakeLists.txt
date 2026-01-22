cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(qtils REQUIRED CONFIG)
find_package(Boost REQUIRED)
find_package(fmt REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE qtils::qtils fmt::fmt Boost::boost)
set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 20
    CXX_STANDARD_REQUIRED ON
)
