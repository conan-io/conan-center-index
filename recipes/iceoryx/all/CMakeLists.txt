cmake_minimum_required(VERSION 3.5)
project(cmake_wrapper

if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
  find_package(acl REQUIRED)
  if(TARGET acl::acl)
    add_library(acl ALIAS acl::acl)
  endif()
endif()

add_subdirectory("iceoryx_meta")
