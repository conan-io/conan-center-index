cmake_minimum_required(VERSION 3.1)
project(test_package C)

find_package(CURL REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} CURL::libcurl)
if(APPLE)
  find_library(CORE_FOUNDATION CoreFoundation)
  target_link_libraries(${PROJECT_NAME} ${CORE_FOUNDATION})
endif()
