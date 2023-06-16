cmake_minimum_required(VERSION 3.8)
project(test_package)

find_package(Platform.Delegates)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} Platform.Delegates::Platform.Delegates)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 17)
