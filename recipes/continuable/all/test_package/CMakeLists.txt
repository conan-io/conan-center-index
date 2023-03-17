cmake_minimum_required(VERSION 3.1)
project(test_package)

find_package(continuable REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
set_target_properties(
    ${PROJECT_NAME} PROPERTIES

    CXX_STANDARD 14
    CXX_STANDARD_REQUIRED ON
)
target_link_libraries(${PROJECT_NAME} PRIVATE continuable::continuable)
