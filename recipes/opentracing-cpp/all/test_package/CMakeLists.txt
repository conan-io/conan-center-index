cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(OpenTracing REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)

if(TARGET OpenTracing::opentracing-static)
  target_link_libraries(${PROJECT_NAME} PRIVATE OpenTracing::opentracing-static)
else()
  target_link_libraries(${PROJECT_NAME} PRIVATE OpenTracing::opentracing)
endif()

