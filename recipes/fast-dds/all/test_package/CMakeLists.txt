cmake_minimum_required(VERSION 3.1)
project(HelloWorldExample)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(fastdds REQUIRED)

include_directories(msg)

add_executable(test_pub
    HelloWorld_pub.cpp
    msg/HelloWorld.cxx
    msg/HelloWorldPublisher.cpp
    msg/HelloWorldPubSubTypes.cxx
    msg/HelloWorldSubscriber.cpp
)

add_executable(test_sub
    HelloWorld_sub.cpp
    msg/HelloWorld.cxx
    msg/HelloWorldPublisher.cpp
    msg/HelloWorldPubSubTypes.cxx
    msg/HelloWorldSubscriber.cpp
)

set_property(TARGET test_sub PROPERTY CXX_STANDARD 11)
set_property(TARGET test_pub PROPERTY CXX_STANDARD 11)

target_link_libraries(test_sub
    fastrtps
)

target_link_libraries(test_pub
    fastrtps
)
