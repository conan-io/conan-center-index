cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(date CONFIG REQUIRED)

add_executable(example src/example.cpp)
target_link_libraries(example date::date)
set_property(TARGET example PROPERTY CXX_STANDARD 11)
if(DATE_HEADER_ONLY)
  target_compile_definitions(example PRIVATE DATE_HEADER_ONLY)
endif()
