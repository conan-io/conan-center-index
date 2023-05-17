cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(fastdds REQUIRED CONFIG)

add_executable(${PROJECT_NAME}
    test_package.cpp
    msg/HelloWorld.cxx
    msg/HelloWorldPubSubTypes.cxx
)

target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
target_link_libraries(${PROJECT_NAME} fastrtps)
