cmake_minimum_required(VERSION 3.8)

project(test_package LANGUAGES CXX)

find_package(exprtk REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)

target_link_libraries(${PROJECT_NAME} PRIVATE exprtk::exprtk)

if (MSVC)
   # Compile will fail without this flag
   # TODO should this be something added into conan recipe?
   target_compile_options(${PROJECT_NAME} PRIVATE "/bigobj")
endif (MSVC)
