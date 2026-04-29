cmake_minimum_required(VERSION 3.12)
project(cmake_wrapper)

if (CMAKE_CXX_STANDARD LESS 17)
  set(CMAKE_CXX_STANDARD 17)
endif()
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(acl)
if(acl_FOUND)
  link_libraries(acl::acl)
endif()

add_subdirectory(src/iceoryx_meta)
