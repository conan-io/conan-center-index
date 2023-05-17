cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Libwebsockets REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(TARGET websockets_shared)
  target_link_libraries(${PROJECT_NAME} websockets_shared)
else()
  target_link_libraries(${PROJECT_NAME} websockets)
endif()
set_property(TARGET ${PROJECT_NAME} PROPERTY C_STANDARD 99)
