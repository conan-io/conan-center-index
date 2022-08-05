cmake_minimum_required(VERSION 3.1)
project(test_package C)

file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/../test_package/logo.png
     DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(zstd REQUIRED)

add_executable(${PROJECT_NAME} ${CMAKE_CURRENT_SOURCE_DIR}/../test_package/test_package.c)
if (TARGET zstd::libzstd_shared)
  target_link_libraries(${PROJECT_NAME} zstd::libzstd_shared)
else()
  target_link_libraries(${PROJECT_NAME} zstd::libzstd_static)
endif()
