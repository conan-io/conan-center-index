cmake_minimum_required(VERSION 3.8)
project(LibAesgm LANGUAGES C)

add_library(Aesgm
    #sources
    ${LIBAESGM_SRC_DIR}/aescrypt.c
    ${LIBAESGM_SRC_DIR}/aeskey.c
    ${LIBAESGM_SRC_DIR}/aes_modes.c
    ${LIBAESGM_SRC_DIR}/aes_ni.c
    ${LIBAESGM_SRC_DIR}/aestab.c
    #headers
    ${LIBAESGM_SRC_DIR}/aescpp.h
    ${LIBAESGM_SRC_DIR}/aes.h
    ${LIBAESGM_SRC_DIR}/aes_ni.h
    ${LIBAESGM_SRC_DIR}/aesopt.h
    ${LIBAESGM_SRC_DIR}/aestab.h
    ${LIBAESGM_SRC_DIR}/aes_via_ace.h
    ${LIBAESGM_SRC_DIR}/brg_endian.h
    ${LIBAESGM_SRC_DIR}/brg_types.h
)

target_include_directories(Aesgm
    INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
    $<INSTALL_INTERFACE:include/LibAesgm>
)

if(WIN32 AND BUILD_SHARED_LIBS)
    target_compile_definitions(Aesgm PRIVATE DLL_EXPORT)
endif()

install(TARGETS Aesgm
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(
    FILES
    ${LIBAESGM_SRC_DIR}/aes.h
    ${LIBAESGM_SRC_DIR}/aes_ni.h
    ${LIBAESGM_SRC_DIR}/aes_via_ace.h
    ${LIBAESGM_SRC_DIR}/aescpp.h
    ${LIBAESGM_SRC_DIR}/aesopt.h
    ${LIBAESGM_SRC_DIR}/aestab.h
    ${LIBAESGM_SRC_DIR}/brg_endian.h
    ${LIBAESGM_SRC_DIR}/brg_types.h
    DESTINATION include
)
