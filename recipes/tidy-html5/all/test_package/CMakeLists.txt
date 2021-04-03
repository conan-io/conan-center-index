cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(tidy REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)

if(TARGET tidy::tidy-share)
  target_link_libraries(${PROJECT_NAME} tidy::tidy-share)
else()
  target_link_libraries(${PROJECT_NAME} tidy::tidy-static)
endif()
