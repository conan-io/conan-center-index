cmake_minimum_required(VERSION 3.15)
project(cmake_wrapper)

find_package(cpprestsdk REQUIRED)
find_package(OpenSSL REQUIRED)
find_package(LibXml2 REQUIRED)

link_libraries(
    cpprestsdk::cpprestsdk
    OpenSSL::SSL
    LibXml2::LibXml2
)

find_package(UUID QUIET)
if(UUID_FOUND)
    link_libraries(libuuid::libuuid)
endif()

add_subdirectory(src/Microsoft.WindowsAzure.Storage)
