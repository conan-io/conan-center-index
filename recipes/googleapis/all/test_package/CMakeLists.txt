cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(protobuf REQUIRED CONFIG)
find_package(googleapis REQUIRED CONFIG)


add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} protobuf::protobuf)

protobuf_generate(LANGUAGE cpp TARGET ${PROJECT_NAME} PROTOS ${googleapis_RES_DIRS_RELEASE}/google/type/color.proto)
