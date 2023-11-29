cmake_minimum_required(VERSION 3.12)

project(xmlrpc-epi C)

find_package(EXPAT REQUIRED)

if(MSVC AND BUILD_SHARED_LIBS)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

file(GLOB SOURCES "src/*.c")
file(GLOB PRIVATE_HEADERS "src‌/*_private.h")
set(PUBLIC_HEADERS
    "src/base64.h"
    "src/encodings.h"
    "src/queue.h"
    "src/simplestring.h"
    "src/xml_element.h"
    "src/xml_to_dandarpc.h"
    "src/xml_to_soap.h"
    "src/xmlrpc_introspection.h"
    "src/xmlrpc.h"
)

add_library(xmlrpc-epi)
target_sources(xmlrpc-epi PUBLIC ${PUBLIC_HEADERS} PRIVATE ${SOURCES} ${PRIVATE_HEADER})

set(LINK_LIBRARIES expat::expat)
if (WIN32 OR APPLE)
    find_package(ICONV REQUIRED)
    list(APPEND LINK_LIBRARIES Iconv::Iconv)
endif (WIN32)

target_link_libraries(xmlrpc-epi ${LINK_LIBRARIES})

install(TARGETS xmlrpc-epi)
install(FILES ${PUBLIC_HEADERS} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/xmlrpc-epi)
