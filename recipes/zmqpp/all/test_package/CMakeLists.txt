cmake_minimum_required(VERSION 3.1)
project(test_package)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(Threads REQUIRED)
find_package(ZeroMQ REQUIRED)
find_package(zmqpp REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)

if(ZMQPP_BUILD_SHARED)
  target_link_libraries(${PROJECT_NAME} zmqpp zmq sodium Threads::Threads)
else()
  target_link_libraries(${PROJECT_NAME} zmqpp-static zmq sodium Threads::Threads)
endif()

