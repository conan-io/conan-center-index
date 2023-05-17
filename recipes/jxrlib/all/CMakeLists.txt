cmake_minimum_required(VERSION 3.1)
project(jxrlib LANGUAGES C)

include(GNUInstallDirs)
include(TestBigEndian)

if(NOT MSVC)
    add_definitions(-D__ANSI__)
endif()

test_big_endian(ISBIGENDIAN)
if(ISBIGENDIAN)
    set(DEF_ENDIAN _BIG__ENDIAN_)
endif()

include_directories(
    ${JPEGXR_FOLDER}/common/include
    ${JPEGXR_FOLDER}/image/sys
    ${JPEGXR_FOLDER}/jxrgluelib
    ${JPEGXR_FOLDER}/jxrtestlib
)

# JPEG-XR

set(JPEGXR_SOURCES
    ${JPEGXR_FOLDER}/image/sys/adapthuff.c
    ${JPEGXR_FOLDER}/image/sys/image.c
    ${JPEGXR_FOLDER}/image/sys/strcodec.c
    ${JPEGXR_FOLDER}/image/sys/strPredQuant.c
    ${JPEGXR_FOLDER}/image/sys/strTransform.c
    ${JPEGXR_FOLDER}/image/sys/perfTimerANSI.c

    ${JPEGXR_FOLDER}/image/decode/decode.c
    ${JPEGXR_FOLDER}/image/decode/postprocess.c
    ${JPEGXR_FOLDER}/image/decode/segdec.c
    ${JPEGXR_FOLDER}/image/decode/strdec.c
    ${JPEGXR_FOLDER}/image/decode/strInvTransform.c
    ${JPEGXR_FOLDER}/image/decode/strPredQuantDec.c
    ${JPEGXR_FOLDER}/image/decode/JXRTranscode.c

    ${JPEGXR_FOLDER}/image/encode/encode.c
    ${JPEGXR_FOLDER}/image/encode/segenc.c
    ${JPEGXR_FOLDER}/image/encode/strenc.c
    ${JPEGXR_FOLDER}/image/encode/strFwdTransform.c
    ${JPEGXR_FOLDER}/image/encode/strPredQuantEnc.c
)
add_library(jpegxr ${JPEGXR_SOURCES})
set_property(TARGET jpegxr PROPERTY COMPILE_DEFINITIONS DISABLE_PERF_MEASUREMENT ${DEF_ENDIAN})
set_property(TARGET jpegxr PROPERTY LINK_INTERFACE_LIBRARIES "")
install(TARGETS jpegxr
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

# JXR-GLUE

set(JXRGLUE_SOURCES
    ${JPEGXR_FOLDER}/jxrgluelib/JXRGlue.c
    ${JPEGXR_FOLDER}/jxrgluelib/JXRMeta.c
    ${JPEGXR_FOLDER}/jxrgluelib/JXRGluePFC.c
    ${JPEGXR_FOLDER}/jxrgluelib/JXRGlueJxr.c

    ${JPEGXR_FOLDER}/jxrtestlib/JXRTest.c
    ${JPEGXR_FOLDER}/jxrtestlib/JXRTestBmp.c
    ${JPEGXR_FOLDER}/jxrtestlib/JXRTestHdr.c
    ${JPEGXR_FOLDER}/jxrtestlib/JXRTestPnm.c
    ${JPEGXR_FOLDER}/jxrtestlib/JXRTestTif.c
    ${JPEGXR_FOLDER}/jxrtestlib/JXRTestYUV.c
)
add_library(jxrglue ${JXRGLUE_SOURCES})
target_link_libraries(jxrglue jpegxr)
set_property(TARGET jxrglue PROPERTY COMPILE_DEFINITIONS DISABLE_PERF_MEASUREMENT ${DEF_ENDIAN})
set_property(TARGET jxrglue PROPERTY LINK_INTERFACE_LIBRARIES "")
install(TARGETS jxrglue
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(FILES
    ${JPEGXR_FOLDER}/jxrgluelib/JXRGlue.h
    ${JPEGXR_FOLDER}/jxrgluelib/JXRMeta.h
    ${JPEGXR_FOLDER}/jxrtestlib/JXRTest.h
    ${JPEGXR_FOLDER}/image/sys/windowsmediaphoto.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR} COMPONENT Headers
)
install(DIRECTORY ${JPEGXR_FOLDER}/common/include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
  FILES_MATCHING PATTERN "*.h"
)
