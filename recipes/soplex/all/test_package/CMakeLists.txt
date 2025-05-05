cmake_minimum_required(VERSION 3.8)
project(test_package CXX)
set(CMAKE_CXX_STANDARD 14)

find_package(soplex REQUIRED CONFIG)
# work around v1 legacy generators always having namespaces
if(TARGET soplex::soplex)
   add_library(soplex INTERFACE IMPORTED)
   set_target_properties(soplex PROPERTIES INTERFACE_LINK_LIBRARIES soplex::soplex)
endif()

add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE soplex)
