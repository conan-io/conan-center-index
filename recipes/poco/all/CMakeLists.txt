cmake_minimum_required(VERSION 3.5.0)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

if(MYSQL_ROOT_DIR)
  find_package(MySQL REQUIRED)
  add_library(MySQL::client INTERFACE IMPORTED)
  target_link_libraries(MySQL::client INTERFACE MySQL::MySQL)
endif()
if(PostgreSQL_ROOT_DIR)
  find_package(PostgreSQL REQUIRED)
  add_library(PostgreSQL::client INTERFACE IMPORTED)
  target_link_libraries(PostgreSQL::client INTERFACE PostgreSQL::PostgreSQL)
endif()

# Disable automatic linking on MSVC
add_definitions(-DPOCO_NO_AUTOMATIC_LIBS)

if ("${CONAN_PACKAGE_VERSION}" VERSION_GREATER "1.10")
    add_definitions(-DXML_DTD)
endif()


add_subdirectory(src)
