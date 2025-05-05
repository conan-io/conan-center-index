cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(msgpack REQUIRED CONFIG)

# TODO: remove msgpack:: namespace when fixed in cpp_info of recipe
if(MSGPACK_C_API)
  add_executable(${PROJECT_NAME}_c test_package.c)
  target_link_libraries(${PROJECT_NAME}_c msgpack::msgpackc)
endif()
if(MSGPACK_CPP_API)
  add_executable(${PROJECT_NAME}_cpp test_package.cpp)
  target_link_libraries(${PROJECT_NAME}_cpp msgpack::msgpackc-cxx)
  set_property(TARGET ${PROJECT_NAME}_cpp PROPERTY CXX_STANDARD 11)
endif()
