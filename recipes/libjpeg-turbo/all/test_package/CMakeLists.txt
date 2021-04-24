cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(libjpeg-turbo REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if (USE_SHARED)
  target_link_libraries(${PROJECT_NAME} PRIVATE libjpeg-turbo::jpeg)
else()
  target_link_libraries(${PROJECT_NAME} PRIVATE libjpeg-turbo::jpeg-static)
endif()
set_property(TARGET ${PROJECT_NAME} PROPERTY C_STANDARD 99)
