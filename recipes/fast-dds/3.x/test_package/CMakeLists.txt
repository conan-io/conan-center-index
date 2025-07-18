cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(fastdds REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)

target_sources(${PROJECT_NAME} PRIVATE
  msg/HelloWorldPubSubTypes.cxx)

target_include_directories(${PROJECT_NAME} PRIVATE
${CMAKE_CURRENT_SOURCE_DIR}/msg)

target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
target_link_libraries(${PROJECT_NAME} fastdds)
