cmake_minimum_required(VERSION 3.15)
project(cmake_wrapper)

find_package(cpprestsdk REQUIRED)
find_package(OpenSSL REQUIRED)
find_package(LibXml2 REQUIRED)
find_package(UUID QUIET)

add_subdirectory(src/Microsoft.WindowsAzure.Storage)

target_link_libraries(azurestorage
    cpprestsdk::cpprestsdk
    OpenSSL::SSL
    LibXml2::LibXml2
    $<TARGET_NAME_IF_EXISTS:libuuid::libuuid>
)
