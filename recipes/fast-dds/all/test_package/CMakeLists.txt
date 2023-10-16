cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(fastdds REQUIRED CONFIG)

add_executable(${PROJECT_NAME}
    test_package.cpp
)

if(fastcdr_VERSION VERSION_GREATER_EQUAL "2.0.0")
target_sources(${PROJECT_NAME}
    PRIVATE
    msg/v2/HelloWorld.cxx
    msg/v2/HelloWorldPubSubTypes.cxx
)
else()
target_sources(${PROJECT_NAME}
    PRIVATE
    msg/v1/HelloWorld.cxx
    msg/v1/HelloWorldPubSubTypes.cxx
)
endif()

target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
target_link_libraries(${PROJECT_NAME} fastrtps)
