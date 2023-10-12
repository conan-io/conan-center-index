project(cmake_wrapper)

find_package(LibXML2 REQUIRED)

set(LibXML2_INCLUDE_DIR ${libxml2_INCLUDE_DIRS})

add_subdirectory("Microsoft.WindowsAzure.Storage")
