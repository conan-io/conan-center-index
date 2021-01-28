cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(rabbitmq-c REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(RABBITMQ_SHARED)
  target_link_libraries(${PROJECT_NAME} rabbitmq::rabbitmq)
else()
  target_link_libraries(${PROJECT_NAME} rabbitmq::rabbitmq-static)
endif()

if(WITH_SSL)
  list(APPEND test_compile_definitions WITH_SSL)
endif()

target_compile_definitions(${PROJECT_NAME} PRIVATE ${test_compile_definitions})
