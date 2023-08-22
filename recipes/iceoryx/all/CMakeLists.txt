cmake_minimum_required(VERSION 3.16)
project(cmake_wrapper)

if(TARGET acl::acl)
  add_library(acl ALIAS acl::acl)
endif()

add_subdirectory("iceoryx_meta")
