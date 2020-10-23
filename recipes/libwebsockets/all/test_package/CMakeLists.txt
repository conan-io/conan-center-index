cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(Libwebsockets REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
# TODO: remove Libwebsockets:: namespace when fixed in cpp_info of recipe
if(LIBWEBSOCKETS_SHARED)
  target_link_libraries(${PROJECT_NAME} Libwebsockets::websockets_shared)
else()
  target_link_libraries(${PROJECT_NAME} Libwebsockets::websockets)
endif()
set_property(TARGET ${PROJECT_NAME} PROPERTY C_STANDARD 99)
