cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(sockpp CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE $<IF:$<TARGET_EXISTS:Sockpp::sockpp>,Sockpp::sockpp,Sockpp::sockpp-static>)
