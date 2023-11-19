cmake_minimum_required(VERSION 3.15)
project(libecwj2 VERSION 3.3)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD 98)
set(CMAKE_CXX_EXTENSIONS OFF)

set(SRC_FILES
    C/NCSEcw/NCSEcw/NCSAffineTransform.cpp
    C/NCSEcw/NCSEcw/NCSBlockFile.cpp
    C/NCSEcw/NCSEcw/NCSEcw.cpp
    C/NCSEcw/NCSEcw/NCSFile.cpp
    C/NCSEcw/NCSEcw/NCSHuffmanCoder.cpp
    C/NCSEcw/NCSEcw/NCSWorldFile.cpp
    C/NCSEcw/NCSEcw/ncscbm.c
    C/NCSEcw/NCSEcw/ncscbmidwt.c
    C/NCSEcw/NCSEcw/ncscbmnet.c
    C/NCSEcw/NCSEcw/ncscbmopen.c
    C/NCSEcw/NCSEcw/ncscbmpurge.c
    C/NCSEcw/NCSJP2/NCSJP2.cpp
    C/NCSEcw/NCSJP2/NCSJP2BitsPerComponentBox.cpp
    C/NCSEcw/NCSJP2/NCSJP2Box.cpp
    C/NCSEcw/NCSJP2/NCSJP2CaptureResolutionBox.cpp
    C/NCSEcw/NCSJP2/NCSJP2ChannelDefinitionBox.cpp
    C/NCSEcw/NCSJP2/NCSJP2ColorSpecificationBox.cpp
    C/NCSEcw/NCSJP2/NCSJP2ComponentMappingBox.cpp
    C/NCSEcw/NCSJP2/NCSJP2ContiguousCodestreamBox.cpp
    C/NCSEcw/NCSJP2/NCSJP2DataEntryURLBox.cpp
    C/NCSEcw/NCSJP2/NCSJP2DefaultDisplayResolutionBox.cpp
    C/NCSEcw/NCSJP2/NCSJP2File.cpp
    C/NCSEcw/NCSJP2/NCSJP2FileTypeBox.cpp
    C/NCSEcw/NCSJP2/NCSJP2FileView.cpp
    C/NCSEcw/NCSJP2/NCSJP2GMLGeoLocationBox.cpp
    C/NCSEcw/NCSJP2/NCSJP2HeaderBox.cpp
    C/NCSEcw/NCSJP2/NCSJP2ImageHeaderBox.cpp
    C/NCSEcw/NCSJP2/NCSJP2IntellectualPropertyBox.cpp
    C/NCSEcw/NCSJP2/NCSJP2PCSBox.cpp
    C/NCSEcw/NCSJP2/NCSJP2PaletteBox.cpp
    C/NCSEcw/NCSJP2/NCSJP2ResolutionBox.cpp
    C/NCSEcw/NCSJP2/NCSJP2SignatureBox.cpp
    C/NCSEcw/NCSJP2/NCSJP2SuperBox.cpp
    C/NCSEcw/NCSJP2/NCSJP2UUIDBox.cpp
    C/NCSEcw/NCSJP2/NCSJP2UUIDInfoBox.cpp
    C/NCSEcw/NCSJP2/NCSJP2UUIDListBox.cpp
    C/NCSEcw/NCSJP2/NCSJP2WorldBox.cpp
    C/NCSEcw/NCSJP2/NCSJP2XMLBox.cpp
    C/NCSEcw/NCSJP2/NCSJPC.cpp
    C/NCSEcw/NCSJP2/NCSJPCBuffer.cpp
    C/NCSEcw/NCSJP2/NCSJPCCOCMarker.cpp
    C/NCSEcw/NCSJP2/NCSJPCCODMarker.cpp
    C/NCSEcw/NCSJP2/NCSJPCCOMMarker.cpp
    C/NCSEcw/NCSJP2/NCSJPCCRGMarker.cpp
    C/NCSEcw/NCSJP2/NCSJPCCodeBlock.cpp
    C/NCSEcw/NCSJP2/NCSJPCCodingStyleParameter.cpp
    C/NCSEcw/NCSJP2/NCSJPCComponent.cpp
    C/NCSEcw/NCSJP2/NCSJPCComponentDepthType.cpp
    C/NCSEcw/NCSJP2/NCSJPCDCShiftNode.cpp
    C/NCSEcw/NCSJP2/NCSJPCDump.cpp
    C/NCSEcw/NCSJP2/NCSJPCEOCMarker.cpp
    C/NCSEcw/NCSJP2/NCSJPCEPHMarker.cpp
    C/NCSEcw/NCSJP2/NCSJPCEcwpIOStream.cpp
    C/NCSEcw/NCSJP2/NCSJPCFileIOStream.cpp
    C/NCSEcw/NCSJP2/NCSJPCICCNode.cpp
    C/NCSEcw/NCSJP2/NCSJPCIOStream.cpp
    C/NCSEcw/NCSJP2/NCSJPCMCTNode.cpp
    C/NCSEcw/NCSJP2/NCSJPCMQCoder.cpp
    C/NCSEcw/NCSJP2/NCSJPCMainHeader.cpp
    C/NCSEcw/NCSJP2/NCSJPCMarker.cpp
    C/NCSEcw/NCSJP2/NCSJPCMemoryIOStream.cpp
    C/NCSEcw/NCSJP2/NCSJPCNode.cpp
    C/NCSEcw/NCSJP2/NCSJPCNodeTiler.cpp
    C/NCSEcw/NCSJP2/NCSJPCPLMMarker.cpp
    C/NCSEcw/NCSJP2/NCSJPCPLTMarker.cpp
    C/NCSEcw/NCSJP2/NCSJPCPOCMarker.cpp
    C/NCSEcw/NCSJP2/NCSJPCPPMMarker.cpp
    C/NCSEcw/NCSJP2/NCSJPCPPTMarker.cpp
    C/NCSEcw/NCSJP2/NCSJPCPacket.cpp
    C/NCSEcw/NCSJP2/NCSJPCPacketLengthType.cpp
    C/NCSEcw/NCSJP2/NCSJPCPaletteNode.cpp
    C/NCSEcw/NCSJP2/NCSJPCPrecinct.cpp
    C/NCSEcw/NCSJP2/NCSJPCProgression.cpp
    C/NCSEcw/NCSJP2/NCSJPCProgressionOrderType.cpp
    C/NCSEcw/NCSJP2/NCSJPCQCCMarker.cpp
    C/NCSEcw/NCSJP2/NCSJPCQCDMarker.cpp
    C/NCSEcw/NCSJP2/NCSJPCQuantizationParameter.cpp
    C/NCSEcw/NCSJP2/NCSJPCRGNMarker.cpp
    C/NCSEcw/NCSJP2/NCSJPCResample.cpp
    C/NCSEcw/NCSJP2/NCSJPCResolution.cpp
    C/NCSEcw/NCSJP2/NCSJPCSIZMarker.cpp
    C/NCSEcw/NCSJP2/NCSJPCSOCMarker.cpp
    C/NCSEcw/NCSJP2/NCSJPCSODMarker.cpp
    C/NCSEcw/NCSJP2/NCSJPCSOPMarker.cpp
    C/NCSEcw/NCSJP2/NCSJPCSOTMarker.cpp
    C/NCSEcw/NCSJP2/NCSJPCSegment.cpp
    C/NCSEcw/NCSJP2/NCSJPCSubBand.cpp
    C/NCSEcw/NCSJP2/NCSJPCT1Coder.cpp
    C/NCSEcw/NCSJP2/NCSJPCTLMMarker.cpp
    C/NCSEcw/NCSJP2/NCSJPCTagTree.cpp
    C/NCSEcw/NCSJP2/NCSJPCTilePartHeader.cpp
    C/NCSEcw/NCSJP2/NCSJPCYCbCrNode.cpp
    C/NCSEcw/shared_src/build_pyr.c
    C/NCSEcw/shared_src/collapse_pyr.c
    C/NCSEcw/shared_src/compress.cpp
    C/NCSEcw/shared_src/ecw_open.c
    C/NCSEcw/shared_src/ecw_read.c
    C/NCSEcw/shared_src/fileio_compress.c
    C/NCSEcw/shared_src/fileio_decompress.c
    C/NCSEcw/shared_src/pack.c
    C/NCSEcw/shared_src/qmf_util.c
    C/NCSEcw/shared_src/quantize.c
    C/NCSEcw/shared_src/unpack.c
    C/NCSGDT2/NCSGDTEPSGKey.cpp
    C/NCSGDT2/NCSGDTEpsg.cpp
    C/NCSGDT2/NCSGDTLocation.cpp
    C/NCSUtil/CNCSBase64Coder.cpp
    C/NCSUtil/NCSBase64.cpp
    C/NCSUtil/NCSError.cpp
    C/NCSUtil/NCSEvent.cpp
    C/NCSUtil/NCSLog.cpp
    C/NCSUtil/NCSMutex.cpp
    C/NCSUtil/NCSObject.cpp
    C/NCSUtil/NCSPrefs.cpp
    C/NCSUtil/NCSPrefsXML.cpp
    C/NCSUtil/NCSString.cpp
    C/NCSUtil/NCSThread.cpp
    C/NCSUtil/dynamiclib.c
    C/NCSUtil/error.c
    C/NCSUtil/file.c
    C/NCSUtil/log.cpp
    C/NCSUtil/malloc.c
    C/NCSUtil/mutex.c
    C/NCSUtil/pool.c
    C/NCSUtil/prefs.c
    C/NCSUtil/queue.c
    C/NCSUtil/thread.c
    C/NCSUtil/timer.c
    C/NCSUtil/util.c
    C/NCSnet/NCScnet3/NCSGetPasswordDlg.cpp
    C/NCSnet/NCScnet3/NCSGetRequest.cpp
    C/NCSnet/NCScnet3/NCSPostRequest.cpp
    C/NCSnet/NCScnet3/NCSProxy.cpp
    C/NCSnet/NCScnet3/NCSRequest.cpp
    C/NCSnet/NCScnet3/NCSSocket.cpp
    C/NCSnet/NCScnet3/NCScnet.cpp
)
if (MSVC)
    list(APPEND SRC_FILES
        C/NCSEcw/NCSEcw/NCSOutputFile.cpp
        C/NCSEcw/NCSEcw/NCSRenderer.cpp
        C/NCSUtil/CNCSMetabaseEdit.cpp
        C/NCSUtil/CNCSMultiSZ.cpp
        C/NCSUtil/NCSCoordinateConverter.cpp
        C/NCSUtil/NCSCoordinateSystem.cpp
        C/NCSUtil/NCSCoordinateTransform.cpp
        C/NCSUtil/NCSCrypto.cpp
        C/NCSUtil/NCSExtent.cpp
        C/NCSUtil/NCSExtents.cpp
        C/NCSUtil/NCSObjectList.cpp
        C/NCSUtil/NCSPoint.cpp
        C/NCSUtil/NCSPrefsWin.cpp
        C/NCSUtil/NCSRasterCoordinateConverter.cpp
        C/NCSUtil/NCSScreenPoint.cpp
        C/NCSUtil/NCSServerState.cpp
        C/NCSUtil/NCSWorldPoint.cpp
        C/NCSUtil/exception_catch.c
        C/NCSUtil/main.c
        C/NCSUtil/quadtree.cpp
        C/NCSnet/NCScnet2/NCSWinHttp.c
        C/NCSnet/NCScnet2/NCScnet.c
        C/NCSnet/NCScnet2/cnet2util.c
        C/NCSnet/NCScnet2/connect.c
        C/NCSnet/NCScnet2/packet.c
        libecwj2.def
    )
endif()

add_library(libecwj2 STATIC ${SRC_FILES})
target_include_directories(libecwj2 PRIVATE include)

#add_compile_options(-Wall -Wno-long-long -fno-common)

find_package(JPEG REQUIRED CONFIG)
find_package(tinyxml REQUIRED CONFIG)

target_link_libraries(libecwj2 PRIVATE JPEG::JPEG tinyxml::tinyxml)

target_compile_definitions(libecwj2 PRIVATE
    HAVE_STDLIB_H=1
    PACKAGE_NAME=libecwj2
    "$<$<CONFIG:Release>:NDEBUG>"
    "$<$<CONFIG:Debug>:_DEBUG>"
)
if(MSVC)
    target_compile_definitions(libecwj2 PRIVATE WIN32 _WINDOWS _LIB UNICODE _UNICODE LIBECWJ2 QT_DLL)
    target_compile_options(libecwj2 PRIVATE
        "$<$<CONFIG:Release>:/W3;/O2>"
        "$<$<CONFIG:Debug>:/W3;/GZ;/Od>"
    )
    # link_libraries(imagehlp version Crypt32 shlwapi ws2_32 kernel32 user32 gdi32 comdlg32 advapi32 shell32 ole32 oleaut32 uuid imm32 winmm wsock32 winspool)
    if(BUILD_SHARED_LIBS)
        target_compile_definitions(libecwj2 PRIVATE _USRDLL LIBECWJ2)
    else()
        target_compile_definitions(libecwj2 PRIVATE _LIB NCSECW_STATIC_LIBS)
    endif()
elseif(UNIX AND NOT APPLE)
    target_compile_options(libecwj2 PRIVATE -pthread
        -includeNCSArray.h
        -includeNCSDefs.h
        -includeNCSDynamicLib.h
        -includeNCSMalloc.h
        -includeNCSMemPool.h
        -includeNCSMutex.h
        -includeNCSTimeStamp.h
        -includeNCSTypes.h
    )
    target_compile_definitions(libecwj2 PRIVATE POSIX=1 LINUX=1 _GNU_SOURCE _REENTRANT _LARGEFILE64_SOURCE PATH_MAX=4096)
    target_link_libraries(libecwj2 PRIVATE m dl rt)
elseif(APPLE)
    target_compile_definitions(libecwj2 PRIVATE MACOSX)
endif()

install(TARGETS libecwj2
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)
install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/include/ DESTINATION include)
