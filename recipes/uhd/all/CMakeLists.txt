cmake_minimum_required(VERSION 3.12)
project(uhd_wrapper)

set(CMAKE_CXX_STANDARD 17)

find_package(acl)
if(acl_FOUND)
  link_libraries(acl::acl)
endif()

add_subdirectory(uhd)
