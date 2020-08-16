cmake_minimum_required(VERSION 3.1)
project(PvrTcCompressor)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(WIN32 AND BUILD_SHARED_LIBS)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

set(HDRS_FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/AlphaBitmap.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/BitScale.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/BitUtility.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/Bitmap.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/ColorRgba.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/Interval.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/MortonTable.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/Point2.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/PvrTcDecoder.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/PvrTcEncoder.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/PvrTcPacket.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/RgbBitmap.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/RgbaBitmap.h
)
set(SRCS_FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/BitScale.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/MortonTable.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/PvrTcDecoder.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/PvrTcEncoder.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/PvrTcPacket.cpp
)
add_library(pvrtccompressor ${SRCS_FILES})
target_include_directories(pvrtccompressor PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder)

install(TARGETS pvrtccompressor
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)
install(FILES ${HDRS_FILES} DESTINATION include)
