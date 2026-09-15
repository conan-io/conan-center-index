cmake_minimum_required(VERSION 3.15)
project(librtmp LANGUAGES C)

include(GNUInstallDirs)

find_package(ZLIB REQUIRED)
find_package(OpenSSL REQUIRED)

set(RTMP_LIB_SRC_DIR ${RTMP_SRC_DIR}/librtmp)

add_library(rtmp
    ${RTMP_LIB_SRC_DIR}/amf.c
    ${RTMP_LIB_SRC_DIR}/hashswf.c
    ${RTMP_LIB_SRC_DIR}/log.c
    ${RTMP_LIB_SRC_DIR}/parseurl.c
    ${RTMP_LIB_SRC_DIR}/rtmp.c
)
target_include_directories(rtmp PRIVATE ${RTMP_LIB_SRC_DIR})
target_link_libraries(rtmp
    PRIVATE
        ZLIB::ZLIB
        OpenSSL::Crypto
        OpenSSL::SSL
        $<$<BOOL:${WIN32}>:ws2_32>
        $<$<BOOL:${WIN32}>:winmm>
)
set_target_properties(rtmp PROPERTIES
    VERSION ${RTMP_VERSION}
    SOVERSION ${RTMP_SOVERSION}
    WINDOWS_EXPORT_ALL_SYMBOLS TRUE
)

set(RTMP_PUBLIC_HEADERS
    ${RTMP_LIB_SRC_DIR}/amf.h
    ${RTMP_LIB_SRC_DIR}/http.h
    ${RTMP_LIB_SRC_DIR}/log.h
    ${RTMP_LIB_SRC_DIR}/rtmp.h
)

install(FILES ${RTMP_PUBLIC_HEADERS} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/librtmp)
install(
    TARGETS rtmp
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
