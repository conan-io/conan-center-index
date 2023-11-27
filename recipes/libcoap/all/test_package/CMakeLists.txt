cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(libcoap REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(TARGET libcoap::coap-3)
    target_link_libraries(${PROJECT_NAME} libcoap::coap-3)
else()
    target_link_libraries(${PROJECT_NAME} libcoap::coap)
endif()
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
