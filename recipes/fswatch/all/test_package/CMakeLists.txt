cmake_minimum_required(VERSION 3.12)
project(test_package LANGUAGES CXX)

find_package(fswatch REQUIRED CONFIG)
find_package(Threads REQUIRED)

if(MACOS)
  find_library(COREFOUNDATION_LIBRARY CoreFoundation REQUIRED)
  find_library(CORESERVICES_LIBRARY CoreServices REQUIRED)
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE fswatch::fswatch Threads::Threads)

if(MACOS)
  target_link_libraries(${PROJECT_NAME} PRIVATE ${COREFOUNDATION_LIBRARY} ${CORESERVICES_LIBRARY})
endif()
