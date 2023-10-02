cmake_minimum_required(VERSION 3.8)
project(test_package)

find_package(nghttp3 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE nghttp3::nghttp3)
