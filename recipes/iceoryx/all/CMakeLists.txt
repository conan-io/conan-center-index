cmake_minimum_required(VERSION 3.12)
project(cmake_wrapper)

find_package(acl)
if(acl_FOUND)
  link_libraries(acl::acl)
endif()

add_subdirectory(src/iceoryx_meta)
