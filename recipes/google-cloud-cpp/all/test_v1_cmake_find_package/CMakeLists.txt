cmake_minimum_required(VERSION 3.5)
project(google-cloud-cpp-quickstart CXX C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(google-cloud-cpp REQUIRED)

add_executable(storage storage.cpp)
target_link_libraries(storage google-cloud-cpp::storage)

add_executable(pubsub pubsub.cpp)
target_link_libraries(pubsub google-cloud-cpp::pubsub)
